"""Turn the raw HIPE machine files into data/processed/HIPE/<N>, N being the number of machines summed into the total.

The recording is split by month: October tunes, November trains, December is reported.
- phases*.csv: the same total as aggregate*.csv, but as active and reactive power on each phase, which any
  three-phase plant meter reports. Not clipped: a phase can read negative.
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
PHASE_COLUMNS = ["P1_kW", "P2_kW", "P3_kW", "Q1_kvar", "Q2_kvar", "Q3_kvar"]
# Each meter's phases L1, L2, L3 in the HighTemperatureOven meter's labels, found by correlating their phase voltages
# over October. Every meter not listed is wired L1, L2, L3. The PhaseCount_2 meters are single-phase and have no
# per-phase columns: their P_kW and Q_kvar go on the one phase listed.
WIRING = {"ChipPress": (1, 0, 2), "PickAndPlaceUnit": (0,), "ScreenPrinter": (2,), "VacuumPump2": (1,)}


def read_times(df: pd.DataFrame) -> np.ndarray:
    """Return one machine's times (UTC, no time zone).

    - Each timestamp's UTC offset (its "+02:00" ending) is applied, so the clock does not jump back an hour when
      summer time ends; that jump would cut the series.
    - The series stops at the first timestamp not later than the one before: that sample, the one before it and
      all later ones are dropped."""
    time = pd.to_datetime(df.SensorDateTime, utc=True, format="ISO8601").dt.tz_localize(None).to_numpy()
    stop = np.flatnonzero(np.diff(time) <= 0 * SECOND)
    return time[: stop[0] if stop.size else len(time)]


def read_machine(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return one machine's times, as read_times, and power, negatives set to 0."""
    time = read_times(df)
    power = df.P_kW.to_numpy(dtype=float)[: len(time)]
    return time, np.where(power < 0, 0.0, power)


def read_phases(df: pd.DataFrame, wiring: tuple[int, ...] = (0, 1, 2)) -> tuple[np.ndarray, np.ndarray]:
    """Return one machine's times, as read_times, and its readings (T, 6) in PHASE_COLUMNS order, on the reference
    phases: own phase i goes to wiring[i]. A meter without per-phase columns has its P_kW and Q_kvar on own phase 1."""
    time = read_times(df)
    own = np.zeros((len(time), 6))
    if "P1_kW" in df:
        own[:] = df[PHASE_COLUMNS].to_numpy(dtype=float)[: len(time)]
    else:
        own[:, 0], own[:, 3] = df.P_kW.to_numpy(dtype=float)[: len(time)], df.Q_kvar.to_numpy(dtype=float)[: len(time)]
    out = np.zeros_like(own)
    for i, ph in enumerate(wiring):
        out[:, [ph, 3 + ph]] += own[:, [i, 3 + i]]
    return time, out


def interp1_extrap(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    """Linear interpolation that also extrapolates.

    - Inside the samples: np.interp, exact at the samples (scipy's interp1d is not, in some versions).
    - Outside: the line through the first two, or the last two, samples."""
    y = np.interp(x, xp, fp)
    lo, hi = x < xp[0], x > xp[-1]
    y[lo] = fp[0] + (x[lo] - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0])
    y[hi] = fp[-1] + (x[hi] - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    return y


def machine_phases(path: Path, grid: np.ndarray) -> np.ndarray:
    """One machine's readings (T, 6) on the grid's times (process()'s timestamps), interpolated and rounded as there."""
    df = pd.read_csv(path, usecols=lambda c: c in {"SensorDateTime", "P_kW", "Q_kvar", *PHASE_COLUMNS})
    t, x = read_phases(df, WIRING.get(path.stem.split("_PhaseCount")[0], (0, 1, 2)))
    at, xp = (grid - grid[0]) / SECOND, (t - grid[0]) / SECOND  # grid[0] is process()'s start
    return np.round(np.column_stack([interp1_extrap(at, xp, c) for c in x.T]), 4) + 0.0


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
    files = sorted((a.raw / "Equipment").glob("*.csv"))  # machine k is the k-th, as in read_equipment_csv
    order, grid = [*range(2, len(files) + 1), 1], eq.timestamp.to_numpy()
    phases = machine_phases(files[order[0] - 1], grid)
    for n in range(2, sums.shape[1] + 1):
        out, tune = a.out / str(n), a.tuning_out / str(n)
        phases = phases + machine_phases(files[order[n - 1] - 1], grid)  # one machine at a time: the files are large
        tables = {
            "aggregate": pd.DataFrame({"timestamp": eq.timestamp, "active_power": sums[:, n - 1]}),
            "equipment": eq.iloc[:, : n + 1],
            "states": st.iloc[:, : n + 1],
            "phases": pd.DataFrame({"timestamp": eq.timestamp, **dict(zip(PHASE_COLUMNS, phases.T, strict=True))}),
        }
        training = draw_training(pool, rng)
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
