"""Self-check of hart_inspired.py on a hand-made example: python3 src/hart_inspired/test_hart_inspired.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from hart_inspired import events, main

N = np.nan
# written one line per machine A..E over samples 0..15; .T makes rows samples
states = np.array(
    [
        # A: 1..4 and 12..13 estimated (B, then E, switch inside), ON again at the last event
        [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # B: 2..3 estimated
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # C: 6..10, D turns OFF at the same sample 11
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],  # D: 8..10, C switches OFF with it
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # E: ON from the start, never estimated
    ]
).T
agg = np.array([5, 15, 18, 18.5, 15.5, 5.25, 9, 12, 14, 13, 11.5, 2, 6, 3, 1, 7])
expected = np.array(
    [
        [0, 10.25, 10.25, 10.25, 10.25, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, N],  # |agg[5] - agg[4]|, then |agg[14] - agg[13]|
        [0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # |agg[4] - agg[3]| while ON
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

with tempfile.TemporaryDirectory() as name:
    tmp = Path(name)
    time = (pd.Timestamp("2017-10-23") + pd.to_timedelta(np.arange(16), unit="s")).strftime("%d-%b-%Y %H:%M:%S")
    data = tmp / "data" / "HIPE" / "5"
    data.mkdir(parents=True)
    pd.DataFrame({"timestamp": time, "active_power": agg}).to_csv(data / "aggregate.csv", index=False)
    pd.DataFrame({"timestamp": time, **{f"Eq{j}_State": states[:, j] for j in range(5)}}).to_csv(
        data / "states.csv", index=False
    )
    main(["--dataset", "hipe", "--machines", "5", "--data-root", str(tmp / "data"), "--results-root", str(tmp)])
    text = (tmp / "HIPE" / "5.csv").read_text()
    out = pd.read_csv(tmp / "HIPE" / "5.csv")

assert text.splitlines()[0] == "timestamp,active_power,Estimate_0,Estimate_1,Estimate_2,Estimate_3,Estimate_4"
assert text.splitlines()[1] == "23-Oct-2017 00:00:00,5.0,0.0,0.0,0.0,0.0,NaN"
assert list(out.timestamp) == list(time) and np.array_equal(out.active_power, agg)
assert np.array_equal(out.iloc[:, 2:].to_numpy(), expected, equal_nan=True)

print("ok")
