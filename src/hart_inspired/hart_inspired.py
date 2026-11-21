"""Hart-inspired oracle-state baseline, port of src/hart_inspired/hart_inspired.m: estimates each machine's power from
the step in the aggregate at its OFF event. It reads the TRUE on/off states, so it is an oracle-state reference, not an
unsupervised NILM method. It runs on the unsplit tables.
Output: timestamp, active_power (the aggregate), then one estimate per machine, NaN where none was made.

Example: python3 src/hart_inspired/hart_inspired.py --dataset hipe --machines 9
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def events(states: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Events of hart_inspired.m: per machine the sample after each state change (find(diff ~= 0) + 1) and its sign
    (+1 ON, -1 OFF), machine after machine, then stably sorted by sample like MATLAB's sort. 0-based sample, machine."""
    d = np.diff(states.astype(int), axis=0)
    machine, sample = np.nonzero(d.T)  # row-major over d.T: machine by machine, samples ascending
    order = np.argsort(sample, kind="stable")
    return sample[order] + 1, machine[order], d[sample, machine][order]


def estimate(states: np.ndarray, agg: np.ndarray, sample, machine, change) -> np.ndarray:
    """estimation_using_2_samples_OFF_event.m: for each ON event whose next event of the same machine is OFF, if the
    other machines' states are equal at the ON and OFF samples and at the OFF sample and the one before it, the machine
    gets |agg[OFF] - agg[OFF - 1]| from the ON sample to the OFF sample, both included. Elsewhere 0 when OFF and NaN
    when ON. As in the MATLAB while loop, the last event is never visited."""
    est = np.where(states == 1, np.nan, 0.0)
    for i in range(len(sample) - 1):
        if change[i] != 1:
            continue
        m = machine[i]
        later = np.flatnonzero(machine[i + 1 :] == m)  # next event of the same machine
        if not later.size or change[i + 1 + later[0]] != -1:
            continue
        on, off = sample[i], sample[i + 1 + later[0]]
        others = np.arange(states.shape[1]) != m
        if np.array_equal(states[on, others], states[off, others]) and np.array_equal(
            states[off - 1, others], states[off, others]
        ):
            est[on : off + 1, m] = abs(agg[off] - agg[off - 1])
    return est


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    parser.add_argument("--machines", type=int, required=True)
    parser.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    parser.add_argument("--results-root", type=Path, default=REPO / "results" / "hart_inspired")
    a = parser.parse_args(argv)
    data = a.data_root / a.dataset.upper() / str(a.machines)
    out = a.results_root / a.dataset.upper() / f"{a.machines}.csv"

    agg = pd.read_csv(data / "aggregate.csv", dtype={"timestamp": str})
    states = pd.read_csv(data / "states.csv").iloc[:, 1:].to_numpy()
    est = estimate(states, agg.active_power.to_numpy(), *events(states))
    out.parent.mkdir(parents=True, exist_ok=True)
    names = [f"Estimate_{j}" for j in range(states.shape[1])]
    pd.concat([agg, pd.DataFrame(est, columns=names)], axis=1).to_csv(out, index=False, na_rep="NaN")


if __name__ == "__main__":
    main()
