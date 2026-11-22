"""Turn the raw HIPE machine files into data/processed/HIPE/<N>, N being the number of machines summed into the total.

The recording is split by month: October tunes, November trains, December is reported.
- data/processed/HIPE/<N>: test rows are December.
- --tuning-out: test rows are October, and every other file links to data/processed/HIPE/<N>. So a method tuned
  with --data-root tuning/data trains and is scored without December. Only the whole-recording files include it.

Example: python3 src/preprocessing/hipe.py [--raw DIR] [--out DIR] [--tuning-out DIR] [--seed 1]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from common import REPO, draw_training, read_equipment_csv, write_csv

# A machine is on when its power is > 0 kW, after clipping negatives to 0, linear resampling to 1 s and rounding to
# 4 decimals (0.1 W).
ON_THRESHOLD_KW = 0
# Cuts in UTC: tuning before TUNING_END, training up to REPORT_START, the reported test after it.
TUNING_END, REPORT_START = np.datetime64("2017-11-01"), np.datetime64("2017-12-01")
# Rows within GAP_S of a cut go to no split. Rows inside a longer gap between two raw samples of a machine are
# dropped, so every kept row inside a machine's own time range is interpolated from samples at most GAP_S apart.
# In the data, every other gap is at most 219 s.
GAP_S = 300

SECOND = np.timedelta64(1, "s")


def read_machine(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return one machine's times (UTC, no time zone) and power.

    - Each timestamp's UTC offset (its "+02:00" ending) is applied, so the clock does not jump back an hour when
      summer time ends; that jump would cut the series.
    - The series stops at the first timestamp not later than the one before: that sample, the one before it and
      all later ones are dropped.
    - Negative power is set to 0."""
    time = pd.to_datetime(df.SensorDateTime, utc=True, format="ISO8601").dt.tz_localize(None)
    time, power = time.to_numpy(), df.P_kW.to_numpy(dtype=float)
    stop = np.flatnonzero(np.diff(time) <= 0 * SECOND)
    n = stop[0] if stop.size else len(time)
    return time[:n], np.where(power[:n] < 0, 0.0, power[:n])


def interp1_extrap(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    """Linear interpolation that also extrapolates.

    - Inside the samples: np.interp, exact at the samples (scipy's interp1d is not, in some versions).
    - Outside: the line through the first two, or the last two, samples."""
    y = np.interp(x, xp, fp)
    lo, hi = x < xp[0], x > xp[-1]
    y[lo] = fp[0] + (x[lo] - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0])
    y[hi] = fp[-1] + (x[hi] - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    return y


def process(folder: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Put every machine on one grid of seconds.

    Returns power (timestamp, Eq<k>_P_kW) and states (timestamp, Eq<k>_State).

    - The grid spans every machine. Each is interpolated linearly onto it, and extrapolated outside its own range.
    - Machines 2..M, then machine 1: it was always off in the one-week release, which dropped it, so the first N
      machines stay the same as there.
    - Rows inside a gap of more than GAP_S between two samples of any machine are dropped for every machine, since
      interpolation would invent them."""
    machines = [read_machine(df) for df in read_equipment_csv(folder, ["SensorDateTime", "P_kW"])]
    start, end = min(t[0] for t, _ in machines), max(t[-1] for t, _ in machines)
    grid = start + np.arange((end - start) // SECOND + 1) * SECOND
    x = (grid - start) / SECOND
    eq, st = pd.DataFrame({"timestamp": grid}), pd.DataFrame({"timestamp": grid})
    for k in [*range(2, len(machines) + 1), 1]:  # columns keep the original equipment numbers
        t, p = machines[k - 1]
        eq[f"Eq{k}_P_kW"] = np.round(interp1_extrap(x, (t - start) / SECOND, p), 4) + 0.0  # + 0.0: -0.0 becomes 0.0
        st[f"Eq{k}_State"] = (eq[f"Eq{k}_P_kW"] > ON_THRESHOLD_KW).astype(np.uint8)
    keep = np.ones(len(grid), dtype=bool)
    for t, _ in machines:
        for i in np.flatnonzero(np.diff(t) > GAP_S * SECOND):
            keep[np.searchsorted(grid, t[i], "right") : np.searchsorted(grid, t[i + 1], "left")] = False
    return eq[keep].reset_index(drop=True), st[keep].reset_index(drop=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw", type=Path, default=REPO / "data" / "raw" / "HIPE")
    parser.add_argument("--out", type=Path, default=REPO / "data" / "processed" / "HIPE")
    parser.add_argument("--tuning-out", type=Path, default=REPO / "tuning" / "data" / "HIPE")
    parser.add_argument("--seed", type=int, default=1)
    a = parser.parse_args(argv)
    rng = np.random.default_rng(a.seed)  # one stream for every training draw

    eq, st = process(a.raw / "Equipment")
    t, gap = eq.timestamp.to_numpy(), GAP_S * SECOND
    tuning = np.flatnonzero(TUNING_END - t > gap)  # rows within GAP_S of a cut belong to no split
    pool = np.flatnonzero((t - TUNING_END >= gap) & (REPORT_START - t > gap))
    report = np.flatnonzero(t - REPORT_START >= gap)
    sums = np.cumsum(eq.iloc[:, 1:].to_numpy(), axis=1)  # column n - 1: total of the first n machines, added in order
    for n in range(2, sums.shape[1] + 1):
        out, tune = a.out / str(n), a.tuning_out / str(n)
        tables = {
            "aggregate": pd.DataFrame({"timestamp": eq.timestamp, "active_power": sums[:, n - 1]}),
            "equipment": eq.iloc[:, : n + 1],
            "states": st.iloc[:, : n + 1],
        }
        training = draw_training(pool, tables["aggregate"].active_power, rng)
        for name, df in tables.items():
            write_csv(df, out / f"{name}.csv")
            write_csv(df.iloc[training], out / f"{name}_training.csv")
            write_csv(df.iloc[report], out / f"{name}_validation.csv")
            write_csv(df.iloc[tuning], tune / f"{name}_validation.csv")
            for f in (f"{name}.csv", f"{name}_training.csv"):
                (tune / f).unlink(missing_ok=True)
                (tune / f).symlink_to((out / f).resolve())


if __name__ == "__main__":
    main()
