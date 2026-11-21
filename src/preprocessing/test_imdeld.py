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


def make_raw(raw: Path, days: list[str], seed: int = 0) -> None:
    """Raw IMDELD-like csv files at about 1 Hz, one entry of days per day: "good", "short" (2000 samples, fails the
    sample-count rule) or "idle" (full day with a median under 10 W but a mean above, fails the median rule).
    Each file drops the first and its own random seconds, and has duplicated seconds and NaNs."""
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
        df = pd.DataFrame(dict(zip(imdeld.UNITS, values, strict=True)), dtype="Int64")
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
    """Disjoint, same rows in the three tables, floor(n_bin * 0.7) / floor(n_bin * 0.3) rows from every bin over 100."""
    agg = pd.read_csv(out / "aggregate.csv").active_power.to_numpy()
    edges = agg.mean() + np.arange(-3, 4) * agg.std(ddof=1)
    counts = np.histogram(agg, edges)[0]
    n_bin = min(1000 * 0.7, counts[counts > 100].min())
    for split, share in [("training", 0.7), ("validation", 0.3)]:
        tables = [pd.read_csv(out / f"{name}_{split}.csv") for name in ["aggregate", "on_off", "equipment"]]
        assert all(tables[0].iloc[:, 0].equals(t.iloc[:, 0]) for t in tables)
        per_bin = np.histogram(tables[0].active_power, edges)[0]
        assert list(per_bin) == [int(np.floor(n_bin * share)) * (c > 100) for c in counts]
    training, validation = (
        pd.read_csv(out / f"aggregate_{split}.csv").timestamp for split in ["training", "validation"]
    )
    assert not set(training) & set(validation)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        raw, out = Path(tmp) / "raw", Path(tmp) / "out"
        make_raw(raw, ["good", "short", "idle", "good"])
        imdeld.main(["--raw", str(raw), "--out", str(out)])
        imdeld.main(["--raw", str(raw), "--out", str(out), "--equipment", "1,2,3,4,5,6,7,8"])
        six, eight = out / "data_6_equipment", out / "data_8_equipment"

        # layout and headers
        names = ["aggregate", "on_off", "equipment"]
        files = [f"{n}{s}.csv" for n in names for s in ["", "_training", "_validation"]]
        assert sorted(p.name for p in six.iterdir()) == sorted(files)
        machines = [1, 2, 3, 4, 7, 8]
        states = ["State DPCI", "State DPCII", "State EFI", "State EFII", "State PI", "State PII"]
        assert header(six / "aggregate.csv") == ["timestamp", "active_power"]
        for s in ["_training", "_validation"]:
            assert header(six / f"aggregate{s}.csv") == ["timestamp", *imdeld.UNITS, "power_factor"]
        for s in ["", "_training", "_validation"]:
            assert header(six / f"on_off{s}.csv") == ["Timestamp", *states]
            assert header(six / f"equipment{s}.csv") == ["timestamp", *[f"active_power_{k}" for k in machines]]
        assert (six / "aggregate.csv").read_text().split("\n")[1].startswith("21-Feb-2018 00:00:00,")
        some = np.array([0, 86399, 86400 * 40 + 3723, 86400 * 400 + 7], dtype=float) + 1519171200
        assert list(time_strings(pd.to_datetime(some, unit="s"))) == list(
            pd.to_datetime(some, unit="s").strftime(TIME_FORMAT)
        )

        # kept days: the short and the idle day are gone, the others have every second
        equipment, on_off = pd.read_csv(six / "equipment.csv"), pd.read_csv(six / "on_off.csv")
        when = pd.to_datetime(equipment.timestamp, format=TIME_FORMAT)
        days = when.dt.normalize().value_counts().sort_index().to_dict()
        assert days == {START: 86400, START + pd.Timedelta(days=3): 86400}
        assert (when.diff().dropna() != pd.Timedelta(seconds=1)).sum() == 1
        a6 = pd.read_csv(six / "aggregate.csv")
        assert equipment.timestamp.equals(on_off.Timestamp) and equipment.timestamp.equals(a6.timestamp)
        assert (equipment.iloc[:, 1:] >= 0).all().all() and (a6.active_power >= 0).all()
        assert (pd.read_csv(six / "aggregate_training.csv").iloc[:, 1:6] >= 0).all().all()
        assert np.array_equal(on_off.iloc[:, 1:].to_numpy(), (equipment.iloc[:, 1:].to_numpy() > 5).astype(int))

        # split: per-bin budget, disjoint, rows in the order drawn by a fresh default_rng(seed)
        check_split(six)
        check_split(eight)
        training = split_train_validation(a6.active_power, 0.7, np.random.default_rng(1))[0]
        drawn = a6.timestamp.iloc[training].reset_index(drop=True)
        assert pd.read_csv(six / "aggregate_training.csv").timestamp.equals(drawn)

        # all eight machines: LVDB-3 added to LVDB-2, unit by unit
        assert pd.read_csv(eight / "on_off.csv").columns[-4:-2].tolist() == ["State MI", "State MII"]
        t = seconds(when)
        lvdb3 = imdeld.read_lvdb_csv(raw / "millingmachine-subcircuit.csv", t)
        assert lvdb3.active_power.mean() > 1000
        assert np.allclose(pd.read_csv(eight / "aggregate.csv").active_power - a6.active_power, lvdb3.active_power)

        # hand check against a direct computation: machines' mean per second, common, without NaN, on the kept days
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
        assert x[j + 749] > t[86399]  # its window reaches into the next kept day
        assert np.isclose(equipment.active_power_1[t == x[j]].item(), y[j - 750 : j + 750].mean(), rtol=1e-9)
        smoothed = pd.Series(y).rolling(1500, center=True, min_periods=1).mean().to_numpy()
        assert np.isclose(smoothed[j], y[j - 750 : j + 750].mean())
        missing = np.setdiff1d(t, x)
        assert missing[0] == t[0]
        interpolated = make_interp_spline(x, smoothed)  # not-a-knot cubic, as MATLAB spline
        for m in [missing[0], missing[len(missing) // 2]]:  # second 0 (extrapolated) and one inside
            assert np.isclose(equipment.active_power_1[t == m].item(), max(interpolated(m), 0), rtol=1e-9)
    print("ok")


if __name__ == "__main__":
    main()
