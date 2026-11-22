"""Self-check of imdeld.py on synthetic raw data: python3 -W error src/preprocessing/test_imdeld.py"""

import tempfile
from pathlib import Path

import imdeld
import numpy as np
import pandas as pd
from common import TIME_FORMAT, read_equipment_csv, seconds, split_train_validation, time_strings
from scipy.interpolate import make_interp_spline

FILES = [
    "doublepolecontactor-I",
    "doublepolecontactor-II",
    "exhaustfan-I",
    "exhaustfan-II",
    "millingmachine-I",
    "millingmachine-II",
    "pelletizer-I",
    "pelletizer-II",
]
START = pd.Timestamp("2018-02-21")
UNITS = ["active_power", "reactive_power", "apparent_power", "current", "voltage"]  # the raw columns


def make_raw(raw: Path, days: list[str], seed: int = 0) -> None:
    """Write raw IMDELD-like files at about 1 Hz (8 machines, 2 subcircuit meters). days gives each day's kind:
    - "good";
    - "short": 2000 samples, fails the sample-count rule;
    - "idle": full day with a median under 10 W but a mean above, fails the median rule.
    Each file misses its first second and its own random seconds, and has repeated seconds and NaNs."""
    rng = np.random.default_rng(seed)
    n = 86400 * len(days)
    iso = np.datetime_as_string(np.datetime64(START, "s") + np.arange(n), "s")
    stamps = np.char.add(np.char.replace(iso, "T", " "), "-03")  # "2018-02-21 00:00:00-03"
    second = np.arange(n) % 86400
    kind = np.repeat(days, 86400)
    (raw / "Equipment").mkdir(parents=True)

    def write(path, level, phase):
        on = np.sin(2 * np.pi * (second / 14400 + phase)) > -0.3  # about 4 h cycles, ON ~60 % of the time
        p = np.where(on, level, 0.02 * level) * (1 + 0.05 * rng.standard_normal(n))
        idle = kind == "idle"
        p[idle] = rng.uniform(0, 4, idle.sum()) + 100 * (rng.random(idle.sum()) < 0.3)  # median ~3 W, mean ~32 W
        keep = (rng.random(n) > 0.001) & ~((kind == "short") & (second >= 2000))
        keep[0] = False  # the first second is filled by spline extrapolation
        rows = np.flatnonzero(keep)
        rows = np.sort(np.concatenate([rows, rng.choice(rows, 200)]))  # duplicated seconds
        values = p[rows] * np.array([[1], [0.6], [1.2], [0.01], [0.0]]) + np.array([[0], [0], [0], [0], [220]])
        values = np.round(values * (1 + 0.01 * rng.standard_normal(values.shape)))  # whole units: writes 3x faster
        df = pd.DataFrame(dict(zip(UNITS, values, strict=True)), dtype="Int64")
        df.insert(0, "timestamp", stamps[rows])
        df.iloc[rng.choice(len(df), 100), 1:] = pd.NA  # written as empty fields, read back as NaN
        df.to_csv(path, index=False)

    for k, name in enumerate(FILES):
        write(raw / "Equipment" / f"{name}.csv", 300 * (k + 1), k / 8)
    write(raw / "pelletizer-subcircuit.csv", 60000, 0.3)
    write(raw / "millingmachine-subcircuit.csv", 30000, 0.6)


def header(path: Path) -> list[str]:
    return path.read_text().split("\n", 1)[0].split(",")


def check_split(out: Path) -> None:
    """Check the split in out.
    - The three tables have the same rows.
    - Test: whole days minus each day's first and last 750 s.
    - Training: at least 1500 s from test; the same count from every bin over 100 rows of the other days."""
    tables = {}
    for split in ["training", "validation"]:
        tables[split] = [pd.read_csv(out / f"{name}_{split}.csv") for name in ["aggregate", "states", "equipment"]]
        assert all(tables[split][0].iloc[:, 0].equals(t.iloc[:, 0]) for t in tables[split])
    t_tr, t_val = (seconds(pd.to_datetime(tables[s][0].timestamp, format=TIME_FORMAT)) for s in tables)
    days = np.unique(t_val // 86400)
    assert len(t_val) == len(days) * (86400 - 1500) and np.array_equal(t_val, np.sort(t_val))
    i = np.clip(np.searchsorted(t_val, t_tr), 1, len(t_val) - 1)
    assert np.minimum(np.abs(t_tr - t_val[i - 1]), np.abs(t_tr - t_val[i])).min() >= 1500

    agg = pd.read_csv(out / "aggregate.csv")
    t = seconds(pd.to_datetime(agg.timestamp, format=TIME_FORMAT))
    a = agg.active_power[~np.isin(t // 86400, days) & (t % 86400 >= 750) & (t % 86400 < 86400 - 750)]
    edges = a.mean() + np.arange(-2, 3) * a.std(ddof=1)  # the outer bins are open-ended
    counts, per_bin = (
        np.bincount(np.searchsorted(edges, x, side="right"), minlength=6)
        for x in (a, tables["training"][0].active_power)
    )
    assert list(per_bin) == [min(490, counts[counts > 100].min()) * (c > 100) for c in counts]


def check_hand_computed(raw: Path, equipment: pd.DataFrame, t: np.ndarray, machines: list[int]) -> None:
    """Check machine 1 against a direct computation: mean per second, common seconds, no NaN, kept days."""
    raw_tables = read_equipment_csv(raw / "Equipment")
    per_second = pd.concat(
        [
            d.assign(t=imdeld.read_timestamps(d.timestamp)).groupby("t").active_power.mean()
            for d in (raw_tables[k - 1] for k in machines)
        ],
        axis=1,
        join="inner",
    ).dropna()
    rows = per_second[np.isin(np.floor(per_second.index / 86400), np.floor(t[[0, -1]] / 86400))]
    x, y = rows.index.to_numpy(), rows.iloc[:, 0].to_numpy()
    j = np.searchsorted(x, t[86399], side="right") - 1  # last sample of the first day
    assert x[j + 1] - x[j] > 1500  # the next kept day is days later: the window stops at the gap
    assert np.isclose(equipment.active_power_1[t == x[j]].item(), y[j - 750 : j + 1].mean(), rtol=1e-9)
    run = np.cumsum(np.diff(x, prepend=x[0]) > 1500)
    smoothed = pd.Series(y).groupby(run).transform(lambda r: r.rolling(1500, center=True, min_periods=1).mean())
    smoothed = smoothed.to_numpy()
    assert np.isclose(smoothed[j], y[j - 750 : j + 1].mean())
    missing = np.setdiff1d(t, x)
    assert missing[0] == t[0]
    # the same cubic spline as imdeld.py's CubicSpline
    interpolated = make_interp_spline(x, smoothed)
    for m in [missing[0], missing[len(missing) // 2]]:  # second 0 (extrapolated) and one inside
        assert np.isclose(equipment.active_power_1[t == m].item(), max(interpolated(m), 0), rtol=1e-9)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        raw, out = Path(tmp) / "raw", Path(tmp) / "out"
        make_raw(raw, ["good", "short", "idle", "good"])
        imdeld.main(["--raw", str(raw), "--out", str(out)])
        imdeld.main(["--raw", str(raw), "--out", str(out), "--equipment", "1,2,3,4,5,6,7,8"])
        six, eight = out / "6", out / "8"

        # layout and headers
        names = ["aggregate", "states", "equipment"]
        files = [f"{n}{s}.csv" for n in names for s in ["", "_training", "_validation"]]
        assert sorted(p.name for p in six.iterdir()) == sorted(files)
        machines = [1, 2, 3, 4, 7, 8]
        states = ["State DPCI", "State DPCII", "State EFI", "State EFII", "State PI", "State PII"]
        for s in ["", "_training", "_validation"]:
            assert header(six / f"aggregate{s}.csv") == ["timestamp", "active_power"]
            assert header(six / f"states{s}.csv") == ["timestamp", *states]
            assert header(six / f"equipment{s}.csv") == ["timestamp", *[f"active_power_{k}" for k in machines]]
        assert (six / "aggregate.csv").read_text().split("\n")[1].startswith("21-Feb-2018 00:00:00,")
        some = np.array([0, 86399, 86400 * 40 + 3723, 86400 * 400 + 7], dtype=float) + 1519171200
        assert list(time_strings(pd.to_datetime(some, unit="s"))) == list(
            pd.to_datetime(some, unit="s").strftime(TIME_FORMAT)
        )

        # kept days: the short and the idle day are gone, the others have every second
        equipment, on_off = pd.read_csv(six / "equipment.csv"), pd.read_csv(six / "states.csv")
        when = pd.to_datetime(equipment.timestamp, format=TIME_FORMAT)
        days = when.dt.normalize().value_counts().sort_index().to_dict()
        assert days == {START: 86400, START + pd.Timedelta(days=3): 86400}
        assert (when.diff().dropna() != pd.Timedelta(seconds=1)).sum() == 1
        a6 = pd.read_csv(six / "aggregate.csv")
        assert equipment.timestamp.equals(on_off.timestamp) and equipment.timestamp.equals(a6.timestamp)
        assert (equipment.iloc[:, 1:] >= 0).all().all() and (a6.active_power >= 0).all()
        assert (pd.read_csv(six / "aggregate_training.csv").active_power >= 0).all()
        assert np.array_equal(on_off.iloc[:, 1:].to_numpy(), (equipment.iloc[:, 1:].to_numpy() > 5).astype(int))

        # split: whole days, edges left out, same count per bin, rows in the order a fresh default_rng(seed) draws
        check_split(six)
        check_split(eight)
        training = split_train_validation(seconds(when), a6.active_power, 86400, 750, np.random.default_rng(1))[0]
        drawn = a6.timestamp.iloc[training].reset_index(drop=True)
        assert pd.read_csv(six / "aggregate_training.csv").timestamp.equals(drawn)

        # all eight machines: the total is LVDB-2 plus LVDB-3 (milling-machine subcircuit)
        assert pd.read_csv(eight / "states.csv").columns[-4:-2].tolist() == ["State MI", "State MII"]
        t = seconds(when)
        lvdb3 = imdeld.read_lvdb_csv(raw / "millingmachine-subcircuit.csv", t)
        assert lvdb3.mean() > 1000
        assert np.allclose(pd.read_csv(eight / "aggregate.csv").active_power - a6.active_power, lvdb3)

        check_hand_computed(raw, equipment, t, machines)

    # a day whose recording stops or starts 30 min late is dropped, like one with a 30 min hole inside
    day = np.arange(86400.0)
    assert imdeld.find_useful_timestamps(day).size == 86400
    for cut in (day[:-1800], day[1800:], np.r_[day[:40000], day[41800:]]):
        assert imdeld.find_useful_timestamps(cut).size == 0
    print("ok")


if __name__ == "__main__":
    main()
