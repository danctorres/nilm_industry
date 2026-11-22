"""Turn the raw IMDELD files into data/processed/IMDELD/<N>, N being the number of selected machines.
python3 src/preprocessing/imdeld.py [--equipment 1,2,3,4,7,8] [--raw DIR] [--out DIR] [--seed 1]"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from common import REPO, seconds, split_train_validation, write_csv
from scipy.interpolate import CubicSpline

ON_THRESHOLD_W = 5  # on when active power is > 5 W; one threshold for every machine
# Moving-average window in samples (1 s each, so 25 minutes), for the machines and the LVDB (low-voltage
# distribution board) meters of the total, before the spline.
SMOOTHING_WINDOW = 1500
BLOCK_S = 86400  # test rows are whole days
GAP_S = SMOOTHING_WINDOW // 2  # left out at each day edge, so a smoothing window rarely spans both sides

STATE_NAMES = ["State DPCI", "State DPCII", "State EFI", "State EFII", "State MI", "State MII", "State PI", "State PII"]


def read_timestamps(raw: pd.Series | pd.Index) -> np.ndarray:
    """Seconds since 1970 for raw timestamp strings, after cutting their last 3 characters (the "-03" UTC offset:
    3 h behind UTC). Raises if a string does not parse."""
    return seconds(pd.Series(pd.to_datetime([s[:-3].rstrip(".") for s in raw.tolist()], format="ISO8601")))


def mean_per_timestamp(machine: pd.DataFrame) -> pd.Series:
    """Average power per distinct raw timestamp string, indexed by that time in seconds."""
    m = machine.groupby("timestamp", sort=False)["active_power"].mean()
    m.index = read_timestamps(m.index)
    return m


def find_common_timestamps(means: list[pd.Series]) -> np.ndarray:
    """The sorted seconds that every selected machine has at least once."""
    t, n = np.unique(np.concatenate([m.index.to_numpy() for m in means]), return_counts=True)
    return t[n >= len(means)]


def find_useful_timestamps(t: np.ndarray) -> np.ndarray:
    """Keep the days with more than 86400 - 7200 common samples (under 2 h missing) and no gap of 5 s or more."""
    day = np.floor(t / 86400)
    s = pd.Series(t)
    count = s.groupby(day).size()
    max_diff = s.groupby(day).diff().groupby(day).max()  # NaN (day dropped) when a day has a single sample
    useful = count.index[(count > 86400 - 7200) & (max_diff < 5)]
    return t[np.isin(day, useful)]


def construct_date_unit_table(means: list[pd.Series], t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Each machine's mean active power at the seconds t, one column per machine. Drops rows with any NaN."""
    power = np.column_stack([m.reindex(t).to_numpy() for m in means])  # raises if two raw strings parse to one second
    ok = ~np.isnan(power).any(axis=1)
    return t[ok], power[ok]


def smooth_and_fill(x: np.ndarray, y: np.ndarray, xq: np.ndarray) -> np.ndarray:
    """Smooth y (samples at the sorted seconds x, a subset of xq), then fill every second of xq. Negatives become 0.

    - The moving average restarts after every gap longer than its window, so it never mixes days weeks apart.
    - Seconds in x keep the smoothed value. The rest come from a not-a-knot cubic spline (the first two and last two
      pieces are each one cubic), which also extrapolates."""
    gaps = np.flatnonzero(np.diff(x) > SMOOTHING_WINDOW) + 1
    y = np.concatenate(
        [pd.Series(part).rolling(SMOOTHING_WINDOW, center=True, min_periods=1).mean() for part in np.split(y, gaps)]
    )
    present = np.isin(xq, x)
    out = np.empty(len(xq))
    out[present] = y
    out[~present] = CubicSpline(x, y)(xq[~present])
    out[out < 0] = 0
    return out


def interpolate_equipment_data(t: np.ndarray, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Drop idle days, then give every machine a value at every second of the kept days.

    - Idle day: the machines' daily medians average under 10 W.
    - Smoothing runs straight through consecutive kept days, so its window crosses midnight."""
    day = np.floor(t / 86400)
    medians = pd.DataFrame(power).groupby(day).median()
    days = medians.index[medians.mean(axis=1) >= 10].to_numpy()
    keep = np.isin(day, days)
    t, power = t[keep], power[keep]
    full = (days[:, None] * 86400 + np.arange(86400)).ravel()
    return full, np.column_stack([smooth_and_fill(t, p, full) for p in power.T])


def read_lvdb_csv(path: Path, t: np.ndarray) -> np.ndarray:
    """Active power of one LVDB file at every second of t: samples at seconds in t, averaged per second, NaN
    dropped, smoothed and filled."""
    lvdb = pd.read_csv(path, usecols=["timestamp", "active_power"])
    s = read_timestamps(lvdb.timestamp)
    shared = np.isin(s, t)
    m = lvdb.active_power[shared].groupby(s[shared]).mean().dropna()
    return smooth_and_fill(m.index.to_numpy(), m.to_numpy(), t)


def calculate_aggregate(raw: Path, t: np.ndarray, selected: list[int]) -> np.ndarray:
    """The total's active power (the only quantity the methods use): LVDB-2 (pelletizer subcircuit), plus LVDB-3
    (milling-machine subcircuit) when machines 5 and 6 are both selected."""
    aggregate = read_lvdb_csv(raw / "pelletizer-subcircuit.csv", t)
    if 5 in selected and 6 in selected:
        aggregate = aggregate + read_lvdb_csv(raw / "millingmachine-subcircuit.csv", t)
    return aggregate


def save_final_data(
    aggregate: pd.DataFrame, on_off: pd.DataFrame, equipment: pd.DataFrame, rng: np.random.Generator, out: Path
) -> None:
    """Split the rows by whole days (bins from the total) and write to out: full tables, training rows (shuffled)
    and test rows (in time order)."""
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

    # Machine k is the k-th file alphabetically. Only the selected ones are read, one at a time, to limit memory.
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
