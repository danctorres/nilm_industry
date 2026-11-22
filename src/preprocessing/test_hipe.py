"""Self-check of hipe.py on a synthetic raw folder: python3 src/preprocessing/test_hipe.py"""

import tempfile
from pathlib import Path

import hipe
import numpy as np
import pandas as pd
from common import TIME_FORMAT
from hipe import main, process, read_machine

T0 = pd.Timestamp("2017-10-23")
rng = np.random.default_rng(0)


def stamps(seconds, whole):
    """HIPE SensorDateTime strings in local summer time: 7-digit fraction, or whole seconds."""
    t = T0 + pd.to_timedelta(seconds, unit="s")
    return np.where(whole, t.strftime("%Y-%m-%dT%H:%M:%S+02:00"), t.strftime("%Y-%m-%dT%H:%M:%S.%f0+02:00"))


def random_times(a, b, whole):
    """Irregular increasing times in [a, b): gaps of 1 to 6 s when whole, 0.3 to 6 s otherwise."""
    gaps = rng.integers(1, 7, 5000) if whole else rng.uniform(0.3, 6, 5000)
    t = a + np.cumsum(gaps)
    return t[t < b]


def random_power(n):
    """OFF (0, or small negative noise) about 40 % of the time, else 0.5 to 5 kW."""
    p = np.where(rng.random(n) < 0.4, rng.choice([0, -0.01], n), rng.uniform(0.5, 5, n))
    return p.round(5)


def write_raw(folder):
    folder.mkdir(parents=True)
    machines = {}
    # machine 1: always 0 but sets start_time (0 s) and end_time (7300 s); written last
    t = np.concatenate([[0], random_times(0, 7300, True), [7300]])
    machines[1] = t, np.zeros(len(t)), True
    # machine 3: fixed first and last two samples for the extrapolation check, negative powers in between
    t = np.concatenate([[5.25, 7.75], random_times(8, 7000, False), [7000.5, 7001.5]])
    p = rng.uniform(-0.5, 5, len(t))
    p[[0, 1, -2, -1]] = [1.0, 2.0, 3.0, 2.5]
    machines[3] = t, p, False
    # machine 4: whole seconds, one timestamp going back 20 samples before the end
    t = random_times(3, 7200, True)
    t[-20] = t[-21] - 1
    machines[4] = t, random_power(len(t)), True
    # machine 5: 4e-05 kW from 8 to 11 s, on grid points (8 s after a sample of another value): the
    # interpolation must return it exactly, and rounding to 4 decimals makes it 0, so the machine is OFF there
    t = np.concatenate([random_times(3, 7.5, False), [8, 9, 10, 11], random_times(11.5, 7150, False)])
    p = random_power(len(t))
    p[np.isin(t, [8, 9, 10, 11])] = 4e-05
    machines[5] = t, p, False
    for k in [2, 6, 7, 8, 9, 10]:
        whole = k in (2, 7, 9)
        t = random_times(rng.uniform(3, 60), rng.uniform(7000, 7200), whole)
        if k == 6:  # a gap of more than GAP_S across the end of the first hour, where neither hour is usable
            t = t[(t <= 3350) | (t >= 3850)]
        machines[k] = (
            t,
            random_power(len(t)),
            rng.random(len(t)) < 0.5 if k == 2 else whole,
        )  # machine 2 mixes both forms
    for k, (t, p, whole) in machines.items():
        pd.DataFrame({"Id": k, "SensorDateTime": stamps(t, whole), "P_kW": p, "Q_kvar": 0.0}).to_csv(
            folder / f"machine_{k:02d}.csv", index=False
        )
    return machines


def files(out):
    return {str(f.relative_to(out)): f.read_bytes() for f in sorted(out.rglob("*.csv"))}


with tempfile.TemporaryDirectory() as name:
    tmp = Path(name)
    machines = write_raw(tmp / "raw" / "Equipment")
    hipe.TUNING_END, hipe.REPORT_START = np.datetime64("2017-10-22T22:30"), np.datetime64("2017-10-22T23:00")
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "out"), "--tuning-out", str(tmp / "tune")])
    out = tmp / "out"

    # timestamps: UTC, cut before the drop, negative power clipped, and no cut where summer time ends
    dst = pd.DataFrame({"SensorDateTime": ["2017-10-29T02:59:59+02:00", "2017-10-29T02:00:00+01:00"], "P_kW": 1.0})
    assert list(read_machine(dst)[0]) == [np.datetime64("2017-10-29T00:59:59"), np.datetime64("2017-10-29T01:00:00")]
    raw4 = pd.read_csv(tmp / "raw" / "Equipment" / "machine_04.csv")
    t4, p4 = read_machine(raw4)
    assert len(t4) == len(raw4) - 21 and (np.diff(t4) > np.timedelta64(0, "s")).all()
    raw3 = pd.read_csv(tmp / "raw" / "Equipment" / "machine_03.csv")
    t3, p3 = read_machine(raw3)
    assert t3[0] == np.datetime64("2017-10-22T22:00:05.25") and t3[1] == np.datetime64("2017-10-22T22:00:07.75")
    assert (raw3.P_kW < 0).any() and np.array_equal(p3, np.maximum(raw3.P_kW, 0))

    # layout and headers
    eq_cols = [f"Eq{k}_P_kW" for k in [*range(2, 11), 1]]
    st_cols = [f"Eq{k}_State" for k in [*range(2, 11), 1]]
    expected = {}
    for n in range(2, 11):
        for s in ["", "_training", "_validation"]:
            expected[f"{n}/aggregate{s}.csv"] = ["timestamp", "active_power"]
            expected[f"{n}/equipment{s}.csv"] = ["timestamp", *eq_cols[:n]]
            expected[f"{n}/states{s}.csv"] = ["timestamp", *st_cols[:n]]
    written = files(out)
    assert set(written) == set(expected), set(written) ^ set(expected)
    read = {f: pd.read_csv(out / f) for f in expected}
    for f, cols in expected.items():
        assert list(read[f].columns) == cols, f

    # 1 s grid from start_time (machine 1, 0 s) to end_time (machine 1, 7300 s) in UTC, without the rows strictly
    # inside machine 6's gap, written in TIME_FORMAT
    eq, st = process(tmp / "raw" / "Equipment")
    assert eq.timestamp.iloc[0] == pd.Timestamp("2017-10-22 22:00:00")
    t6, grid = machines[6][0], np.arange(7301)
    kept = grid[(grid <= t6[t6 <= 3350].max()) | (grid >= t6[t6 >= 3850].min())]
    assert len(kept) < 7301 - 490 and np.array_equal((eq.timestamp - eq.timestamp.iloc[0]).dt.total_seconds(), kept)
    equipment, states, aggregate = (read[f"10/{f}.csv"] for f in ["equipment", "states", "aggregate"])
    assert equipment.timestamp.iloc[0] == "22-Oct-2017 22:00:00"
    assert equipment.timestamp.iloc[-1] == "23-Oct-2017 00:01:40"
    assert (states.timestamp == equipment.timestamp).all() and (aggregate.timestamp == equipment.timestamp).all()
    assert np.array_equal(equipment[eq_cols], eq[eq_cols])

    # machine 3 is extrapolated linearly (not clamped) from its first two samples (5.25 s, 1 kW), (7.75 s, 2 kW):
    # 1 + (k - 5.25) * 0.4 for k = 0..5, and from its last two (7000.5 s, 3 kW), (7001.5 s, 2.5 kW) to 7300 s
    assert list(equipment.Eq3_P_kW[:6]) == [-1.1, -0.7, -0.3, 0.1, 0.5, 0.9]
    assert equipment.Eq3_P_kW.iloc[-1] == -146.75  # 2.5 - 0.5 * (7300 - 7001.5)
    assert list(states.Eq3_State[:6]) == [0, 0, 0, 1, 1, 1]

    # rounding to 4 decimals, states are power > 0 on the rounded values
    assert list(equipment.Eq5_P_kW[8:12]) == [0.0] * 4 and list(states.Eq5_State[8:12]) == [0] * 4
    values = equipment[eq_cols].to_numpy()
    assert np.array_equal(np.round(values, 4), values)
    assert np.array_equal(states[st_cols].to_numpy(), (values > 0).astype(int))
    assert np.allclose(aggregate.active_power, values.sum(axis=1), rtol=0, atol=1e-9)

    # splits in time, cut here at 22:30 and 23:00 UTC (1 Nov and 1 Dec in the real data), 300 s left out next to each
    # cut: before tunes, between trains, after reports; the tuning copy validates on its own rows and links the rest
    since = (
        pd.to_datetime(equipment.timestamp, format=TIME_FORMAT) - pd.Timestamp("2017-10-22 22:00")
    ).dt.total_seconds()
    since, row = since.to_numpy(), {t: i for i, t in enumerate(equipment.timestamp)}
    for n in range(2, 11):
        assert np.allclose(read[f"{n}/aggregate.csv"].active_power, values[:, :n].sum(axis=1), rtol=0, atol=1e-9)
        tune = tmp / "tune" / str(n)
        for folder, s, expected_rows in (
            (out / str(n), "training", None),
            (out / str(n), "validation", np.flatnonzero(since >= 3900)),
            (tune, "validation", np.flatnonzero(since < 1500)),
        ):
            agg = pd.read_csv(folder / f"aggregate_{s}.csv")
            rows = [row[t] for t in agg.timestamp]
            if expected_rows is None:
                assert rows and all(2100 <= since[r] < 3300 for r in rows)
            else:
                assert rows == list(expected_rows)
            eq_split, st_split = (pd.read_csv(folder / f"{name}_{s}.csv") for name in ("equipment", "states"))
            assert (eq_split.timestamp == agg.timestamp).all() and (st_split.timestamp == agg.timestamp).all()
            assert np.array_equal(eq_split[eq_cols[:n]], values[rows, :n])
            assert np.array_equal(st_split[st_cols[:n]], states[st_cols[:n]].to_numpy()[rows])
            assert np.allclose(agg.active_power, values[rows, :n].sum(axis=1), rtol=0, atol=1e-9)
        for f in ("aggregate.csv", "equipment.csv", "states.csv", "aggregate_training.csv", "states_training.csv"):
            assert (tune / f).is_symlink() and (tune / f).resolve() == (out / str(n) / f).resolve(), f

    # determinism: same seed, same files; another seed, other splits
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "same"), "--tuning-out", str(tmp / "same_tune")])
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "other"), "--tuning-out", str(tmp / "o"), "--seed", "2"])
    assert files(tmp / "same") == written
    other = files(tmp / "other")
    assert other["9/equipment.csv"] == written["9/equipment.csv"]
    assert other["2/aggregate_training.csv"] != written["2/aggregate_training.csv"]

print("ok")
