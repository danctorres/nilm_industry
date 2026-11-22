"""IMDELD preprocessing: raw IMDELD files to data/processed/IMDELD/<N>, N the number of selected machines.
python3 src/preprocessing/imdeld.py [--equipment 1,2,3,4,7,8] [--raw DIR] [--out DIR] [--seed 1]"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from common import REPO, seconds, split_train_validation, write_csv
from scipy.interpolate import CubicSpline

# Methodology choices (values as used in the dissertation)
ON_THRESHOLD_W = 5  # a machine is ON when its active power is > 5 W, one flat threshold for every machine
# moving-average window in samples (1 s each, so 25 minutes), applied to machine and LVDB signals before the spline
SMOOTHING_WINDOW = 1500
BLOCK_S = 86400  # validation holds out whole days
GAP_S = SMOOTHING_WINDOW // 2  # left out at every day edge: no smoothing window spans both sides

STATE_NAMES = ["State DPCI", "State DPCII", "State EFI", "State EFII", "State MI", "State MII", "State PI", "State PII"]


def read_timestamps(raw: pd.Series | pd.Index) -> np.ndarray:
    """Seconds since 1970 of the raw strings without their 3-character suffix (the "-03" UTC offset). Raises if a string
    does not parse."""
    return seconds(pd.Series(pd.to_datetime([s[:-3].rstrip(".") for s in raw.tolist()], format="ISO8601")))


def mean_per_timestamp(machine: pd.DataFrame) -> pd.Series:
    """Mean power per raw timestamp string, indexed by its parsed time in seconds (one entry per unique raw string)."""
    m = machine.groupby("timestamp", sort=False)["active_power"].mean()
    m.index = read_timestamps(m.index)
    return m


def find_common_timestamps(means: list[pd.Series]) -> np.ndarray:
    """The sorted seconds that occur at least once per selected machine."""
    t, n = np.unique(np.concatenate([m.index.to_numpy() for m in means]), return_counts=True)
    return t[n >= len(means)]


def find_useful_timestamps(t: np.ndarray) -> np.ndarray:
    """Keep the days with more than 86400 - 7200 common samples and every gap between consecutive ones under 5 s."""
    day = np.floor(t / 86400)
    s = pd.Series(t)
    count = s.groupby(day).size()
    max_diff = s.groupby(day).diff().groupby(day).max()  # NaN (day dropped) when a day has a single sample
    useful = count.index[(count > 86400 - 7200) & (max_diff < 5)]
    return t[np.isin(day, useful)]


def construct_date_unit_table(means: list[pd.Series], t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Each machine's mean active power at the seconds t (one column per machine), rows with any NaN dropped."""
    power = np.column_stack([m.reindex(t).to_numpy() for m in means])  # raises if two raw strings parse to one second
    ok = ~np.isnan(power).any(axis=1)
    return t[ok], power[ok]


def smooth_and_fill(x: np.ndarray, y: np.ndarray, xq: np.ndarray) -> np.ndarray:
    """Smoothing and filling: y (samples at the sorted seconds x, a subset of xq) smoothed over its samples, kept where
    there is a sample, spline elsewhere, negatives set to 0. The smoothing restarts after every gap longer than its
    window, so it never mixes days weeks apart."""
    gaps = np.flatnonzero(np.diff(x) > SMOOTHING_WINDOW) + 1
    y = np.concatenate(
        [pd.Series(part).rolling(SMOOTHING_WINDOW, center=True, min_periods=1).mean() for part in np.split(y, gaps)]
    )
    present = np.isin(xq, x)
    out = np.empty(len(xq))
    out[present] = y
    out[~present] = CubicSpline(x, y)(xq[~present])  # not-a-knot, extrapolating
    out[out < 0] = 0
    return out


def interpolate_equipment_data(t: np.ndarray, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Drop the days whose daily medians average under 10 W over the machines, then give every machine a value at every
    second of the kept days. The smoothing runs over the kept samples of consecutive kept days in a row, so its window
    crosses midnight."""
    day = np.floor(t / 86400)
    medians = pd.DataFrame(power).groupby(day).median()
    days = medians.index[medians.mean(axis=1) >= 10].to_numpy()
    keep = np.isin(day, days)
    t, power = t[keep], power[keep]
    full = (days[:, None] * 86400 + np.arange(86400)).ravel()
    return full, np.column_stack([smooth_and_fill(t, p, full) for p in power.T])


def read_lvdb_csv(path: Path, t: np.ndarray) -> np.ndarray:
    """Active power of one LVDB file: the samples at the seconds t without NaN, averaged per second, smoothed and filled
    at every second of t."""
    lvdb = pd.read_csv(path, usecols=["timestamp", "active_power"])
    s = read_timestamps(lvdb.timestamp)
    shared = np.isin(s, t)
    m = lvdb.active_power[shared].groupby(s[shared]).mean().dropna()
    return smooth_and_fill(m.index.to_numpy(), m.to_numpy(), t)


def calculate_aggregate(raw: Path, t: np.ndarray, selected: list[int]) -> np.ndarray:
    """The aggregate active power, the only unit the methods use: LVDB-2 (pelletizer subcircuit), plus LVDB-3 (milling
    machine subcircuit) when machines 5 and 6 are both selected."""
    aggregate = read_lvdb_csv(raw / "pelletizer-subcircuit.csv", t)
    if 5 in selected and 6 in selected:
        aggregate = aggregate + read_lvdb_csv(raw / "millingmachine-subcircuit.csv", t)
    return aggregate


def save_final_data(
    aggregate: pd.DataFrame, on_off: pd.DataFrame, equipment: pd.DataFrame, rng: np.random.Generator, out: Path
) -> None:
    """Time-block split of the aggregate, the full tables and their training rows (shuffled) and validation rows (in
    time order) written to out."""
    t = seconds(aggregate.timestamp)
    training, validation = split_train_validation(t, aggregate.active_power, BLOCK_S, GAP_S, rng)
    write_csv(aggregate, out / "aggregate.csv")
    write_csv(on_off, out / "states.csv")
    write_csv(equipment, out / "equipment.csv")
    for name, table in [("aggregate", aggregate), ("states", on_off), ("equipment", equipment)]:
        write_csv(table.iloc[training], out / f"{name}_training.csv")
        write_csv(table.iloc[validation], out / f"{name}_validation.csv")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--equipment", default="1,2,3,4,7,8", help="machine numbers, 1..8 in alphabetical file order")
    p.add_argument("--raw", type=Path, default=REPO / "data" / "raw" / "IMDELD")
    p.add_argument("--out", type=Path, default=REPO / "data" / "processed" / "IMDELD")
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args(argv)
    selected = [int(k) for k in a.equipment.split(",")]
    if not all(1 <= k <= len(STATE_NAMES) for k in selected):
        p.error("--equipment takes machine numbers from 1 to 8")
    rng = np.random.default_rng(a.seed)

    # Machine k is the k-th file alphabetically; only the selected ones are read, one at a time, to bound memory
    files = sorted((a.raw / "Equipment").glob("*.csv"))
    if len(files) != len(STATE_NAMES):
        p.error(f"expected {len(STATE_NAMES)} machine files in {a.raw / 'Equipment'}, found {len(files)}")
    means = [mean_per_timestamp(pd.read_csv(files[k - 1], usecols=["timestamp", "active_power"])) for k in selected]

    t = find_useful_timestamps(find_common_timestamps(means))
    t, power = interpolate_equipment_data(*construct_date_unit_table(means, t))
    timestamp = pd.to_datetime(t, unit="s")

    equipment = pd.DataFrame(power, columns=[f"active_power_{k}" for k in selected])
    equipment.insert(0, "timestamp", timestamp)
    aggregate = pd.DataFrame({"timestamp": timestamp, "active_power": calculate_aggregate(a.raw, t, selected)})
    on_off = pd.DataFrame((power > ON_THRESHOLD_W).astype(int), columns=[STATE_NAMES[k - 1] for k in selected])
    on_off.insert(0, "timestamp", timestamp)
    save_final_data(aggregate, on_off, equipment, rng, a.out / str(len(selected)))


if __name__ == "__main__":
    main()
