"""IMDELD preprocessing, port of the MATLAB main.m: raw IMDELD files to data/processed/IMDELD/<N>, N the number of
selected machines.
python3 src/preprocessing/imdeld.py [--equipment 1,2,3,4,7,8] [--raw DIR] [--out DIR] [--seed 1]"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from common import REPO, matlab_round, movmean, seconds, spline, split_train_validation, write_csv

# Methodology choices (values as used in the dissertation)
ON_THRESHOLD_W = 5  # a machine is ON when its active power is > 5 W, one flat threshold for every machine
# movmean window in samples (1 s each, so 25 minutes) applied to machine and LVDB signals before spline interpolation
SMOOTHING_WINDOW = 1500
TRAINING_RATIO = 0.7  # share of each adaptive bin used for training, the rest for validation

UNITS = ["active_power", "reactive_power", "apparent_power", "current", "voltage"]
STATE_NAMES = ["State DPCI", "State DPCII", "State EFI", "State EFII", "State MI", "State MII", "State PI", "State PII"]


def read_timestamps(raw: pd.Series | pd.Index) -> np.ndarray:
    """posixtime(datetime(t(:, 1:end - 3))): seconds since 1970 of the raw strings without their 3-character suffix
    (the "-03" UTC offset). Raises if a string does not parse."""
    return seconds(pd.Series(pd.to_datetime([s[:-3].rstrip(".") for s in raw.tolist()], format="ISO8601")))


def mean_per_timestamp(machine: pd.DataFrame) -> pd.Series:
    """grpstats(machine, 'timestamp', 'mean', 'DataVars', 'active_power'): mean per raw timestamp string, indexed by
    its parsed time in seconds (one entry per unique raw string, as unique() in find_common_timestamps)."""
    m = machine.groupby("timestamp", sort=False)["active_power"].mean()
    m.index = read_timestamps(m.index)
    return m


def find_common_timestamps(means: list[pd.Series]) -> np.ndarray:
    """find_common_timestamps: the sorted seconds that occur at least once per selected machine."""
    t, n = np.unique(np.concatenate([m.index.to_numpy() for m in means]), return_counts=True)
    return t[n >= len(means)]


def find_useful_timestamps(t: np.ndarray) -> np.ndarray:
    """find_useful_timestamps: keep the days with more than 86400 - 7200 common samples and every gap between
    consecutive ones under 5 s."""
    day = np.floor(t / 86400)
    s = pd.Series(t)
    count = s.groupby(day).size()
    max_diff = s.groupby(day).diff().groupby(day).max()  # NaN (day dropped) when a day has a single sample
    useful = count.index[(count > 86400 - 7200) & (max_diff < 5)]
    return t[np.isin(day, useful)]


def construct_date_unit_table(means: list[pd.Series], t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """construct_date_unit_table(..., 'active_power', ...) then rmmissing: each machine's mean active power at the
    seconds t (one column per machine), rows with any NaN dropped."""
    power = np.column_stack([m.reindex(t).to_numpy() for m in means])  # raises if two raw strings parse to one second
    ok = ~np.isnan(power).any(axis=1)
    return t[ok], power[ok]


def smooth_and_fill(x: np.ndarray, y: np.ndarray, xq: np.ndarray) -> np.ndarray:
    """The movmean + spline step of interpolate_equipment_data and read_lvdb_csv: y (samples at the sorted seconds x,
    a subset of xq) smoothed over its samples, kept where there is a sample, spline elsewhere, negatives set to 0."""
    y = movmean(y, SMOOTHING_WINDOW)
    present = np.isin(xq, x)
    out = np.empty(len(xq))
    out[present] = y
    out[~present] = spline(x, y, xq[~present])
    out[out < 0] = 0  # negative consumption not possible
    return out


def interpolate_equipment_data(t: np.ndarray, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """calculate_metrics_power_day + interpolate_equipment_data: drop the days whose MATLAB-rounded daily medians
    average under 10 W over the machines, then give every machine a value at every second of the kept days.
    The smoothing runs over the kept samples of all days in a row, so its window crosses day boundaries."""
    day = np.floor(t / 86400)
    medians = matlab_round(pd.DataFrame(power).groupby(day).median())
    days = medians.index[medians.mean(axis=1) >= 10].to_numpy()
    keep = np.isin(day, days)
    t, power = t[keep], power[keep]
    full = (days[:, None] * 86400 + np.arange(86400)).ravel()
    return full, np.column_stack([smooth_and_fill(t, p, full) for p in power.T])


def read_lvdb_csv(path: Path, t: np.ndarray) -> pd.DataFrame:
    """read_lvdb_csv for every unit of one LVDB file, read once: per unit, the samples at the seconds t without NaN,
    averaged per second, smoothed and filled at every second of t."""
    lvdb = pd.read_csv(path)
    s = read_timestamps(lvdb.timestamp)
    shared = np.isin(s, t)
    lvdb, s = lvdb[shared], s[shared]
    out = {}
    for unit in UNITS:
        m = lvdb[unit].groupby(s).mean().dropna()
        out[unit] = smooth_and_fill(m.index.to_numpy(), m.to_numpy(), t)
    return pd.DataFrame(out)


def calculate_aggregate_all_feature(raw: Path, t: np.ndarray, selected: list[int]) -> pd.DataFrame:
    """calculate_aggregate_all_feature + calculate_PF: LVDB-2 (pelletizer subcircuit), plus LVDB-3 (milling machine
    subcircuit) unit by unit when machines 5 and 6 are both selected, and the power factor of the sum."""
    aggregate = read_lvdb_csv(raw / "pelletizer-subcircuit.csv", t)
    if 5 in selected and 6 in selected:
        aggregate += read_lvdb_csv(raw / "millingmachine-subcircuit.csv", t)
    aggregate["power_factor"] = aggregate.active_power / aggregate.apparent_power
    return aggregate


def save_final_data(
    aggregate: pd.DataFrame, on_off: pd.DataFrame, equipment: pd.DataFrame, rng: np.random.Generator, out: Path
) -> None:
    """save_final_data: adaptive-binning split of the aggregate active power, the full tables and their
    training / validation rows (in the split's shuffled order) written to out."""
    training, validation = split_train_validation(aggregate.active_power, TRAINING_RATIO, rng)
    write_csv(aggregate.iloc[:, :2], out / "aggregate.csv")
    write_csv(on_off, out / "states.csv")
    write_csv(equipment, out / "equipment.csv")
    for name, table in [("aggregate", aggregate), ("states", on_off), ("equipment", equipment)]:
        write_csv(table.iloc[training], out / f"{name}_training.csv")
        write_csv(table.iloc[validation], out / f"{name}_validation.csv")


def main(argv: list[str] | None = None) -> None:
    """main.m"""
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
    aggregate = calculate_aggregate_all_feature(a.raw, t, selected)
    aggregate.insert(0, "timestamp", timestamp)
    on_off = pd.DataFrame((power > ON_THRESHOLD_W).astype(int), columns=[STATE_NAMES[k - 1] for k in selected])
    on_off.insert(0, "timestamp", timestamp)
    save_final_data(aggregate, on_off, equipment, rng, a.out / str(len(selected)))


if __name__ == "__main__":
    main()
