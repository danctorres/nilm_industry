# Created by danctorres
"""Unsupervised NILM: a neural network splits the aggregate active power into one estimate per machine,
trained only to make the estimates of the ON machines add up to the aggregate.

Example: python3 src/deep_learning/main.py --dataset hipe --mode state --machines 9
"""

import argparse
import csv
from pathlib import Path

import numpy as np
from NN_model.Activation_layer import ActivationLayer, relu, relu_d, tanh_d
from NN_model.Connected_layer import ConnectedLayer
from NN_model.NN import NN

REPO = Path(__file__).resolve().parents[2]
K = 8  # Fourier frequencies


def features(x: np.ndarray) -> np.ndarray:
    """Fourier features of x (n, 1) in [0, 1]: sin and cos of pi k x for k = 1..K, shape (n, 2K).
    Half periods keep the map one-to-one on [0, 1], so the lowest and highest aggregate stay distinct."""
    angle = np.pi * x * np.arange(1, K + 1)
    return np.hstack([np.sin(angle), np.cos(angle)])


def read_csv(path: Path):
    """First column as strings (timestamps), the other columns as a float array."""
    with path.open(newline="") as f:
        rows = list(csv.reader(f))[1:]
    return [r[0] for r in rows], np.array([[float(v) for v in r[1:]] for r in rows])


def load(root: Path, dataset: str, n: int, split: str):
    """Timestamps, aggregate (rows, 1), states (rows, n), equipment power (rows, n)."""
    if dataset == "hipe":
        d = root / "HIPE" / "1_week"
        paths = [
            d / f"aggregate_{split}" / f"agg_{split}_{n}.csv",
            d / f"state_{split}" / f"st_{split}_{n}.csv",
            d / f"equipment_{split}" / f"eq_{split}_{n}.csv",
        ]
    else:
        d = root / "IMDELD" / f"data_{n}_equipment"
        paths = [d / f"aggregate_{split}.csv", d / f"on_off_{split}.csv", d / f"equipment_{split}.csv"]
    timestamps, agg = read_csv(paths[0])
    agg = agg[:, :1]  # active power, further columns are not used
    states, eq = read_csv(paths[1])[1], read_csv(paths[2])[1]
    if states.shape != (len(agg), n) or eq.shape != (len(agg), n):
        raise SystemExit(f"expected {len(agg)} rows and {n} machine columns in {paths[1]} and {paths[2]}")
    states[agg[:, 0] == 0] = 0  # a zero aggregate means every machine is off
    return timestamps, agg, states, eq


def inputs(mode: str, x: np.ndarray, states: np.ndarray) -> np.ndarray:
    if mode == "state":
        return np.hstack([x, states])
    if mode == "fourier":
        return features(x)
    return x


def build(mode: str, n: int, rng: np.random.Generator) -> NN:
    n_in, hidden = {"plain": (1, n + 1), "state": (1 + n, n + 2), "fourier": (2 * K, 20)}[mode]
    return NN(
        [
            ConnectedLayer(n_in, hidden, rng),
            ActivationLayer(relu, relu_d),
            ConnectedLayer(hidden, n, rng),
            ActivationLayer(np.tanh, tanh_d),
        ]
    )


def save(path: Path, timestamps, agg: np.ndarray, est: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            ", ".join(["Timestamp", "Aggregate_Active_Power"] + [f"Estimate_{j}" for j in range(est.shape[1])]) + "\n"
        )
        for ts, a, row in zip(timestamps, agg[:, 0].tolist(), est.tolist(), strict=True):
            f.write(", ".join([ts, str(a)] + [str(v) for v in row]) + "\n")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--mode", choices=["plain", "state", "fourier"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument(
        "--runs", type=int, default=5, help="networks trained from different initial weights, the lowest loss wins"
    )
    p.add_argument("--epochs", type=int, default=1000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, default=REPO / "results" / "deep_learning")
    a = p.parse_args()

    _, agg_tr, st_tr, eq_tr = load(a.data_root, a.dataset, a.machines, "training")
    ts, agg_val, st_val, eq_val = load(a.data_root, a.dataset, a.machines, "validation")

    # Scales come from the training split only. The input is min-max normalised; the target and the
    # estimates share one pure scale, so estimates adding up to agg / hi add up to agg in physical units.
    lo, hi = agg_tr.min(), agg_tr.max()
    x_tr, x_val = inputs(a.mode, (agg_tr - lo) / (hi - lo), st_tr), inputs(a.mode, (agg_val - lo) / (hi - lo), st_val)
    p_min = eq_tr.min(axis=0, keepdims=True) / hi

    rng = np.random.default_rng(a.seed)
    best, best_loss = None, np.inf
    for run in range(a.runs):
        net = build(a.mode, a.machines, rng)
        run_loss = net.train(x_tr, agg_tr / hi, st_tr, p_min, a.epochs)
        print(f"run {run}: mean epoch loss {run_loss:.6g}")
        if best is None or run_loss < best_loss:
            best, best_loss = net, run_loss

    est = best.estimate(x_val) * st_val * hi + 0.0  # OFF machines are zero (+ 0.0 turns -0.0 into 0.0)
    err = est - eq_val
    for j in range(a.machines):
        print(f"machine {j}: MAE {np.mean(np.abs(err[:, j])):.4g}, RMSE {np.sqrt(np.mean(err[:, j] ** 2)):.4g}")

    out = a.results_root / ("HIPE/1_week" if a.dataset == "hipe" else "IMDELD")
    out = (
        out
        / {"plain": "", "state": "states", "fourier": "fourier"}[a.mode]
        / f"estimated_active_power_{a.machines}.csv"
    )
    save(out, ts, agg_val, est)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
