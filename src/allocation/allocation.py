"""Gaussian allocation: each machine draws an independent Gaussian power while ON, and the aggregate is the sum over
the ON machines. The means and variances are fitted by EM from the aggregate and the on/off states alone, and each
machine's estimate is its posterior mean given the aggregate, so the estimates of the ON machines add up to it.
Trains on every unsplit sample outside the validation split, which needs no per-machine power.

Example: python3 src/allocation/allocation.py --dataset hipe --machines 9
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

REPO = Path(__file__).resolve().parents[2]
FLOOR = 1e-6  # variance floor on the aggregate scaled to [0, 1], so the posterior exists when only steady machines run


def posterior(a: np.ndarray, s: np.ndarray, mu: np.ndarray, var: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean and variance of every machine's power given the aggregate a (T,) and the 0/1 states s (T, n); 0 when OFF."""
    total = s @ var + FLOOR
    shift = (a - s @ mu) / total
    return s * (mu + var * shift[:, None]), s * (var - var**2 / total[:, None])


def fit(a: np.ndarray, s: np.ndarray, iters: int = 500) -> tuple[np.ndarray, np.ndarray]:
    """EM for the per-machine means and variances, started from least-squares moments. A machine never ON keeps 0."""
    on = s.any(axis=1)
    a, s = a[on], s[on]
    count = np.maximum(s.sum(axis=0), 1)
    mu = nnls(s, a)[0]
    var = nnls(s, (a - s @ mu) ** 2)[0] + FLOOR
    for _ in range(iters):
        mean, spread = posterior(a, s, mu, var)
        new_mu = mean.sum(axis=0) / count
        var = np.maximum((s * (spread + (mean - new_mu) ** 2)).sum(axis=0) / count, FLOOR)
        converged = np.abs(new_mu - mu).max() < 1e-9
        mu = new_mu
        if converged:
            break
    return mu, var


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, default=REPO / "results" / "allocation")
    a = p.parse_args(argv)
    d = a.data_root / a.dataset.upper() / str(a.machines)

    agg = pd.read_csv(d / "aggregate.csv", usecols=[0, 1])
    states = pd.read_csv(d / "states.csv").iloc[:, 1:].to_numpy(float)
    val = pd.read_csv(d / "aggregate_validation.csv", usecols=[0, 1])
    val_states = pd.read_csv(d / "states_validation.csv").iloc[:, 1:].to_numpy(float)
    if states.shape[1] != a.machines or val_states.shape[1] != a.machines:
        raise SystemExit(f"expected {a.machines} machine columns in {d}")
    train = ~agg.iloc[:, 0].isin(val.iloc[:, 0]).to_numpy()
    power = agg.iloc[:, 1].to_numpy()
    scale = np.abs(power[train]).max() or 1.0

    mu, var = fit(power[train] / scale, states[train])
    for j in range(a.machines):
        print(f"machine {j}: mean {mu[j] * scale:.4g}, sd {np.sqrt(var[j]) * scale:.4g} while ON")
    est = np.maximum(posterior(val.iloc[:, 1].to_numpy() / scale, val_states, mu, var)[0], 0.0) * scale

    out = a.results_root / a.dataset.upper() / f"{a.machines}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([val, pd.DataFrame(est, columns=[f"Estimate_{j}" for j in range(a.machines)])], axis=1).to_csv(
        out, index=False
    )
    print(f"saved {out}")


if __name__ == "__main__":
    main()
