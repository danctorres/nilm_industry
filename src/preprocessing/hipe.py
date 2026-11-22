"""HIPE preprocessing, port of src/preprocessing/HIPE/main.m: turns the raw HIPE machine files into
data/processed/HIPE/<N>, N the number of machines summed into the aggregate.

Example: python3 src/preprocessing/hipe.py [--raw DIR] [--out DIR] [--seed 1]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from common import REPO, matlab_round, read_equipment_csv, seconds, split_train_validation, write_csv

# Methodology choices (values as used in the dissertation)
# a machine is ON when its power is > 0 kW, after clipping negatives, linear resampling to 1 s,
# spline synchronisation and rounding to 4 decimals
ON_THRESHOLD_KW = 0
BLOCK_S = 3600  # validation holds out whole hours
# left out at every block edge; rows inside a longer gap between two raw samples of a machine are dropped, so every
# kept row is interpolated from samples at most GAP_S apart (the others are at most 219 s)
GAP_S = 300

SECOND = np.timedelta64(1, "s")


def read_machine(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Time in UTC and power of one machine (main.m, first loop). The offset is applied, so the week runs on through
    the switch from +02:00 to +01:00 (main.m dropped it and cut the week there). The series is cut at its first
    non-increasing timestamp, the sample before the drop included (Time(stopIndex:end) = []), and negative power is
    set to 0."""
    time = pd.to_datetime(df.SensorDateTime, utc=True, format="ISO8601").dt.tz_localize(None)
    time, power = time.to_numpy(), df.P_kW.to_numpy(dtype=float)
    stop = np.flatnonzero(np.diff(time) <= 0 * SECOND)
    n = stop[0] if stop.size else len(time)
    return time[:n], np.where(power[:n] < 0, 0.0, power[:n])


def interp1_extrap(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    """interp1(xp, fp, x, 'linear', 'extrap'), what retime(..., 'linear') does: np.interp inside, exact at the samples
    (scipy's interp1d is not, depending on its version), and the lines through the first and last two samples
    outside."""
    y = np.interp(x, xp, fp)
    lo, hi = x < xp[0], x > xp[-1]
    y[lo] = fp[0] + (x[lo] - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0])
    y[hi] = fp[-1] + (x[hi] - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    return y


def process(folder: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """main.m up to 'Save data before splitting': equipment power (timestamp, Eq<k>_P_kW) and states
    (timestamp, Eq<k>_State) on start_time:seconds(1):end_time, the span of every machine. retime(..., 'linear') uses
    its default EndValues 'extrap', so outside its own time range a machine is linearly extrapolated. Every machine is
    on the same grid, so synchronize(..., 'union', 'spline') only puts them side by side. Machines 2..M come first and
    machine 1 last: main.m dropped it as always OFF, which holds for the one-week release only, so the first N
    machines are the same as there. Rows inside a gap of more than GAP_S between two samples of any machine are
    dropped from every machine, as interpolation would invent them."""
    machines = [read_machine(df) for df in read_equipment_csv(folder, ["SensorDateTime", "P_kW"])]
    start, end = min(t[0] for t, _ in machines), max(t[-1] for t, _ in machines)
    grid = start + np.arange((end - start) // SECOND + 1) * SECOND
    x = (grid - start) / SECOND
    eq, st = pd.DataFrame({"timestamp": grid}), pd.DataFrame({"timestamp": grid})
    for k in [*range(2, len(machines) + 1), 1]:  # columns keep the original equipment numbers
        t, p = machines[k - 1]
        eq[f"Eq{k}_P_kW"] = matlab_round(interp1_extrap(x, (t - start) / SECOND, p), 4)
        st[f"Eq{k}_State"] = (eq[f"Eq{k}_P_kW"] > ON_THRESHOLD_KW).astype(np.uint8)
    keep = np.ones(len(grid), dtype=bool)
    for t, _ in machines:
        for i in np.flatnonzero(np.diff(t) > GAP_S * SECOND):
            keep[np.searchsorted(grid, t[i], "right") : np.searchsorted(grid, t[i + 1], "left")] = False
    return eq[keep].reset_index(drop=True), st[keep].reset_index(drop=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=REPO / "data" / "raw" / "HIPE")
    parser.add_argument("--out", type=Path, default=REPO / "data" / "processed" / "HIPE")
    parser.add_argument("--seed", type=int, default=1)
    a = parser.parse_args(argv)
    rng = np.random.default_rng(a.seed)  # one stream for every split, as rng(1) in main.m

    eq, st = process(a.raw / "Equipment")
    t = seconds(eq.timestamp)
    sums = np.cumsum(eq.iloc[:, 1:].to_numpy(), axis=1)  # column n - 1: sum of the first n machines, added in order
    for n in range(2, sums.shape[1] + 1):
        agg = pd.DataFrame({"timestamp": eq.timestamp, "active_power": sums[:, n - 1]})
        write_csv(agg, a.out / str(n) / "aggregate.csv")
        write_csv(eq.iloc[:, : n + 1], a.out / str(n) / "equipment.csv")
        write_csv(st.iloc[:, : n + 1], a.out / str(n) / "states.csv")
        training, validation = split_train_validation(t, agg.active_power, BLOCK_S, GAP_S, rng)
        for split, rows in (("training", training), ("validation", validation)):
            write_csv(agg.iloc[rows], a.out / str(n) / f"aggregate_{split}.csv")
            write_csv(eq.iloc[rows, : n + 1], a.out / str(n) / f"equipment_{split}.csv")
            write_csv(st.iloc[rows, : n + 1], a.out / str(n) / f"states_{split}.csv")


if __name__ == "__main__":
    main()
