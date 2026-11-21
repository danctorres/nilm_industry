"""Self-check of hart_inspired.py on a hand-made example: python3 src/hart_inspired/test_hart_inspired.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from hart_inspired import events, main

N = np.nan
# samples 0..15 (rows) of machines A..E (columns)
states = np.array(
    [
        [
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            0,
            1,
        ],  # A: clean 1..4 (B toggles inside and returns), 12..13 disturbed by E, ON again at the last event
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # B: clean 2..3
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # C: 6..10, D turns OFF at the same sample 11
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],  # D: 8..10, C turns OFF in between
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # E: ON from the start, never estimated
    ]
).T
agg = np.array([5, 15, 18, 18.5, 15.5, 5.25, 9, 12, 14, 13, 11.5, 2, 6, 3, 1, 7])
expected = np.array(
    [
        [
            0,
            10.25,
            10.25,
            10.25,
            10.25,
            10.25,
            0,
            0,
            0,
            0,
            0,
            0,
            N,
            N,
            0,
            N,
        ],  # |agg[5] - agg[4]|, the OFF sample 5 included
        [0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # |agg[4] - agg[3]|
        [0, 0, 0, 0, 0, 0, N, N, N, N, N, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, N, N, N, 0, 0, 0, 0, 0],
        [N, N, N, N, N, N, N, N, N, N, N, N, N, 0, 0, 0],
    ]
).T

# events sorted by sample, the tie at sample 11 kept in machine order
sample, machine, change = events(states)
assert list(sample) == [1, 2, 4, 5, 6, 8, 11, 11, 12, 13, 14, 15]
assert list(machine) == [0, 1, 1, 0, 2, 3, 2, 3, 0, 4, 0, 0]
assert list(change) == [1, 1, -1, -1, 1, 1, -1, -1, 1, -1, -1, 1]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    time = (pd.Timestamp("2017-10-23") + pd.to_timedelta(np.arange(16), unit="s")).strftime("%d-%b-%Y %H:%M:%S")
    names = ["Eq2", "Eq3", "Eq4", "Eq5", "Eq6"]
    pd.DataFrame({"Time": time, "P_kW": agg}).to_csv(tmp / "aggregate.csv", index=False)
    pd.DataFrame({"Time": time, **{f"{c}_State": states[:, j] for j, c in enumerate(names)}}).to_csv(
        tmp / "states.csv", index=False
    )
    main(["--data", str(tmp), "--out", str(tmp / "out" / "estimations.csv")])
    text = (tmp / "out" / "estimations.csv").read_text()
    out = pd.read_csv(tmp / "out" / "estimations.csv")

assert text.splitlines()[0] == "Time,P_kW,Eq2_P_kW,Eq3_P_kW,Eq4_P_kW,Eq5_P_kW,Eq6_P_kW"
assert text.splitlines()[1] == "23-Oct-2017 00:00:00,5.0,0.0,0.0,0.0,0.0,NaN"
assert list(out.Time) == list(time) and np.array_equal(out.P_kW, agg)
assert np.array_equal(out.iloc[:, 2:].to_numpy(), expected, equal_nan=True)

print("ok")
