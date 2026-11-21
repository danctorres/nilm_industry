"""Self-check of hipe.py on a synthetic raw folder: python3 src/preprocessing/test_hipe.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from common import matlab_round
from hipe import main, process, read_machine

T0 = pd.Timestamp("2017-10-23")
rng = np.random.default_rng(0)


def stamps(seconds, whole):
    """HIPE SensorDateTime strings: 7-digit fraction, or whole seconds (which hipe.py reads as .02 s)."""
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
    # machine 1: always 0 but sets start_time (00:00:00 -> .02 s) and end_time (7300 s -> 7300.02 s)
    t = np.concatenate([[0], random_times(0, 7300, True), [7300]])
    machines[1] = t, np.zeros(len(t)), True
    # machine 3: fixed first and last two samples for the extrapolation check, negative powers in between
    t = np.concatenate([[5.1234567, 7.6299999], random_times(8, 7000, False), [7000.5, 7001.5]])
    p = rng.uniform(-0.5, 5, len(t))
    p[[0, 1, -2, -1]] = [1.0, 2.0, 3.0, 2.5]
    machines[3] = t, p, False
    # machine 4: whole seconds, one timestamp going back 20 samples before the end
    t = random_times(3, 7200, True)
    t[-20] = t[-21] - 1
    machines[4] = t, random_power(len(t)), True
    # machine 5: 5e-05 kW from 8.02 to 11.02 s, on grid points (8.02 s after a sample of another value): the
    # interpolation must return it exactly, and MATLAB rounds it to 1e-04 where numpy's round gives 0
    t = np.concatenate([random_times(3, 7.5, False), [8.02, 9.02, 10.02, 11.02], random_times(11.5, 7150, False)])
    p = random_power(len(t))
    p[np.isin(t, [8.02, 9.02, 10.02, 11.02])] = 5e-05
    machines[5] = t, p, False
    for k in [2, 6, 7, 8, 9, 10]:
        whole = k in (2, 7, 9)
        t = random_times(rng.uniform(3, 60), rng.uniform(7000, 7200), whole)
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


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    machines = write_raw(tmp / "raw" / "Equipment")
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "out")])
    out = tmp / "out"

    # timestamps: 2-digit fraction, cut before the drop, negative power clipped
    raw4 = pd.read_csv(tmp / "raw" / "Equipment" / "machine_04.csv")
    t4, p4 = read_machine(raw4)
    assert len(t4) == len(raw4) - 21 and (np.diff(t4) > np.timedelta64(0, "s")).all()
    raw3 = pd.read_csv(tmp / "raw" / "Equipment" / "machine_03.csv")
    t3, p3 = read_machine(raw3)
    assert t3[0] == np.datetime64("2017-10-23T00:00:05.12") and t3[1] == np.datetime64("2017-10-23T00:00:07.62")
    assert (raw3.P_kW < 0).any() and np.array_equal(p3, np.maximum(raw3.P_kW, 0))

    # layout and headers
    eq_cols = [f"Eq{k}_P_kW" for k in range(2, 11)]
    st_cols = [f"Eq{k}_State" for k in range(2, 11)]
    expected = {
        "undivided/states.csv": ["Time"] + st_cols,
        "undivided/equipment.csv": ["Time"] + eq_cols,
        "undivided/aggregate.csv": ["Time", "P_kW"],
    }
    for n in range(2, 10):
        for s in ["training", "validation"]:
            expected[f"aggregate_{s}/agg_{s}_{n}.csv"] = ["Time", "P_kW"]
            expected[f"equipment_{s}/eq_{s}_{n}.csv"] = ["Time"] + eq_cols[:n]
            expected[f"state_{s}/st_{s}_{n}.csv"] = ["Time"] + st_cols[:n]
    written = files(out)
    assert set(written) == set(expected), set(written) ^ set(expected)
    read = {f: pd.read_csv(out / f) for f in expected}
    for f, cols in expected.items():
        assert list(read[f].columns) == cols, f

    # 1 s grid from start_time (machine 1, .02 s) to end_time (machine 1, 7300.02 s), written as MATLAB displays it
    eq, st = process(tmp / "raw" / "Equipment")
    assert len(eq) == 7301 and eq.Time.iloc[0] == pd.Timestamp("2017-10-23 00:00:00.02")
    assert (eq.Time.diff().iloc[1:] == pd.Timedelta(1, "s")).all()
    equipment, states, aggregate = (read[f"undivided/{f}.csv"] for f in ["equipment", "states", "aggregate"])
    assert equipment.Time.iloc[0] == "23-Oct-2017 00:00:00" and equipment.Time.iloc[-1] == "23-Oct-2017 02:01:40"
    assert (states.Time == equipment.Time).all() and (aggregate.Time == equipment.Time).all()
    assert np.array_equal(equipment[eq_cols], eq[eq_cols])

    # machine 3 is extrapolated linearly (not clamped) from its first two samples (5.12 s, 1 kW), (7.62 s, 2 kW):
    # 1 + (0.02 + k - 5.12) * 0.4 for k = 0..5, and from its last two (7000.5 s, 3 kW), (7001.5 s, 2.5 kW) to 7300.02 s
    assert list(equipment.Eq3_P_kW[:6]) == [-1.04, -0.64, -0.24, 0.16, 0.56, 0.96]
    assert equipment.Eq3_P_kW.iloc[-1] == -146.76  # 2.5 - 0.5 * (7300.02 - 7001.5)
    assert list(states.Eq3_State[:6]) == [0, 0, 0, 1, 1, 1]

    # MATLAB rounding to 4 decimals, states are power > 0 on the rounded values
    assert list(equipment.Eq5_P_kW[8:12]) == [1e-04] * 4 and list(states.Eq5_State[8:12]) == [1] * 4
    values = equipment[eq_cols].to_numpy()
    assert np.array_equal(matlab_round(values, 4), values)
    assert np.array_equal(states[st_cols].to_numpy(), (values > 0).astype(int))
    assert np.allclose(aggregate.P_kW, values.sum(axis=1), rtol=0, atol=1e-9)

    # splits: disjoint, 70/30, rows aligned with the undivided tables
    row = {t: i for i, t in enumerate(equipment.Time)}
    for n in range(2, 10):
        tr, val = (read[f"aggregate_{s}/agg_{s}_{n}.csv"] for s in ["training", "validation"])
        assert (
            len(val) and not set(tr.Time) & set(val.Time) and 0.41 < len(val) / len(tr) < 0.44
        )  # floor(0.3 n) / floor(0.7 n)
        for s, agg in (("training", tr), ("validation", val)):
            rows = [row[t] for t in agg.Time]
            assert (read[f"equipment_{s}/eq_{s}_{n}.csv"].Time == agg.Time).all()
            assert (read[f"state_{s}/st_{s}_{n}.csv"].Time == agg.Time).all()
            assert np.array_equal(read[f"equipment_{s}/eq_{s}_{n}.csv"][eq_cols[:n]], values[rows, :n])
            assert np.array_equal(read[f"state_{s}/st_{s}_{n}.csv"][st_cols[:n]], states[st_cols[:n]].to_numpy()[rows])
            assert np.allclose(agg.P_kW, values[rows, :n].sum(axis=1), rtol=0, atol=1e-9)

    # determinism: same seed, same files; another seed, other splits
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "same")])
    main(["--raw", str(tmp / "raw"), "--out", str(tmp / "other"), "--seed", "2"])
    assert files(tmp / "same") == written
    other = files(tmp / "other")
    assert other["undivided/equipment.csv"] == written["undivided/equipment.csv"]
    assert other["aggregate_training/agg_training_2.csv"] != written["aggregate_training/agg_training_2.csv"]

print("ok")
