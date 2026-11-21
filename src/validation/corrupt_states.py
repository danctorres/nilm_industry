"""A copy of the processed data with corrupted on/off states, to measure how much the methods depend on exact states.

    python3 src/validation/corrupt_states.py --dataset hipe --machines 9 [--lag S] [--flip P] --out DIR

Writes DIR/<DATASET>/<N>/: the three states files corrupted, every other file a symlink to the original. --lag S:
each state as it was S seconds earlier, a status signal that reports late. --flip P: each entry flipped with
probability P. The training and validation rows are taken from the corrupted unsplit table, so both splits see the
same errors. Then run the methods and validation.py with --data-root DIR."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def corrupt(states: pd.DataFrame, lag: float, flip: float, rng: np.random.Generator) -> pd.DataFrame:
    """states: timestamp in time order, then one 0/1 column per machine. A lag reaching before the first sample, or
    into a gap, reads the first sample after it."""
    t = pd.to_datetime(states.iloc[:, 0], format="%d-%b-%Y %H:%M:%S").to_numpy().astype("datetime64[s]").astype(int)
    v = states.iloc[:, 1:].to_numpy()[np.searchsorted(t, t - lag)]
    v = np.where(rng.random(v.shape) < flip, 1 - v, v)
    return pd.concat([states.iloc[:, :1], pd.DataFrame(v, columns=states.columns[1:])], axis=1)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument("--lag", type=float, default=0, help="seconds each state is reported late")
    p.add_argument("--flip", type=float, default=0, help="probability that a state entry is flipped")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    src, out = (root / a.dataset.upper() / str(a.machines) for root in (a.data_root, a.out))
    out.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.csv"):
        if not f.name.startswith("states") and not (out / f.name).exists():
            (out / f.name).symlink_to(f.resolve())
    full = corrupt(pd.read_csv(src / "states.csv"), a.lag, a.flip, np.random.default_rng(a.seed))
    full.to_csv(out / "states.csv", index=False)
    by_time = full.set_index(full.columns[0])
    for split in ("training", "validation"):
        rows = pd.read_csv(src / f"states_{split}.csv", usecols=[0]).iloc[:, 0]
        by_time.loc[rows].reset_index().to_csv(out / f"states_{split}.csv", index=False)


if __name__ == "__main__":
    main()
