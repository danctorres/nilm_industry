"""Unsupervised NILM: a neural network splits the aggregate active power into one estimate per machine,
trained only to make the estimates of the ON machines add up to the aggregate.

Example: python3 src/deep_learning/main.py --dataset hipe --mode state --machines 9
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from nn import NN, ActivationLayer, ConnectedLayer, relu, relu_d, tanh_d

REPO = Path(__file__).resolve().parents[2]


def load(root: Path, dataset: str, n: int, split: str):
    """Timestamps, aggregate (rows, 1), states (rows, n), equipment power (rows, n)."""
    paths = [root / dataset.upper() / str(n) / f"{name}_{split}.csv" for name in ("aggregate", "states", "equipment")]
    agg, states, eq = (pd.read_csv(path) for path in paths)
    if states.shape != (len(agg), n + 1) or eq.shape != (len(agg), n + 1):
        raise SystemExit(f"expected {len(agg)} rows and {n} machine columns in {paths[1]} and {paths[2]}")
    if not (agg.iloc[:, 0].equals(states.iloc[:, 0]) and agg.iloc[:, 0].equals(eq.iloc[:, 0])):
        raise SystemExit(f"the timestamps of {', '.join(map(str, paths))} differ")
    # copy: for some files pandas hands back a read-only array, and the next line writes to it
    power, states = agg.iloc[:, 1:2].to_numpy(float), states.iloc[:, 1:].to_numpy(float, copy=True)
    states[power[:, 0] == 0] = 0  # a zero aggregate means every machine is off
    return agg.iloc[:, 0], power, states, eq.iloc[:, 1:].to_numpy(float)


def inputs(mode: str, x: np.ndarray, states: np.ndarray) -> np.ndarray:
    return np.hstack([x, states]) if mode == "state" else x


def build(mode: str, n: int, rng: np.random.Generator) -> NN:
    n_in, hidden = {"plain": (1, n + 1), "state": (1 + n, n + 2)}[mode]
    return NN(
        [
            ConnectedLayer(n_in, hidden, rng),
            ActivationLayer(relu, relu_d),
            ConnectedLayer(hidden, n, rng),
            ActivationLayer(np.tanh, tanh_d),
        ]
    )


def save(path: Path, timestamps: pd.Series, agg: np.ndarray, est: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(est, columns=[f"Estimate_{j}" for j in range(est.shape[1])])
    out.insert(0, "Aggregate_Active_Power", agg[:, 0])
    out.insert(0, "Timestamp", timestamps.to_numpy())
    out.to_csv(path, index=False)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--mode", choices=["plain", "state"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument(
        "--runs", type=int, default=5, help="networks trained from different initial weights, the lowest loss wins"
    )
    p.add_argument("--epochs", type=int, default=1000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, default=REPO / "results" / "deep_learning")
    a = p.parse_args(argv)
    if a.runs < 1:
        p.error("--runs must be at least 1")

    _, agg_tr, st_tr, _ = load(a.data_root, a.dataset, a.machines, "training")
    ts, agg_val, st_val, eq_val = load(a.data_root, a.dataset, a.machines, "validation")

    # Scales come from the training split only. The input is min-max normalised; the target and the
    # estimates share one pure scale, so estimates adding up to agg / hi add up to agg in physical units.
    lo, hi = agg_tr.min(), agg_tr.max()
    x_tr, x_val = inputs(a.mode, (agg_tr - lo) / (hi - lo), st_tr), inputs(a.mode, (agg_val - lo) / (hi - lo), st_val)

    rng = np.random.default_rng(a.seed)
    best, best_loss = None, np.inf
    for run in range(a.runs):
        net = build(a.mode, a.machines, rng)
        run_loss = net.train(x_tr, agg_tr / hi, st_tr, a.epochs)
        print(f"run {run}: mean epoch loss {run_loss:.6g}")
        if best is None or run_loss < best_loss:
            best, best_loss = net, run_loss

    est = best.estimate(x_val) * st_val * hi + 0.0  # OFF machines are zero (+ 0.0 turns -0.0 into 0.0)
    err = est - eq_val
    for j in range(a.machines):
        print(f"machine {j}: MAE {np.mean(np.abs(err[:, j])):.4g}, RMSE {np.sqrt(np.mean(err[:, j] ** 2)):.4g}")

    out = a.results_root / a.mode / a.dataset.upper() / f"{a.machines}.csv"
    save(out, ts, agg_val, est)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
