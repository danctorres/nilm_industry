"""Gaussian allocation: while ON, each machine draws its power from its own mixture of Gaussians (an oven idling or
heating, say), independently of the others, and the aggregate is the sum over the ON machines. The components are
fitted by EM from the aggregate and the on/off states alone, and each machine's estimate is its posterior mean given the
aggregate, so the estimates of the ON machines add up to it. --components 1 is a single Gaussian per machine, the method
as first added. Trains on the training split, the same rows as the other methods.

Example: python3 src/allocation/allocation.py --dataset hipe --machines 9
"""

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

REPO = Path(__file__).resolve().parents[2]
FLOOR = 1e-6  # variance floor on the aggregate scaled to [0, 1], so the posterior exists when only steady machines run
CHUNK = 2_000_000  # rows x assignments x machines held at once by `estimate`


def posterior(a: np.ndarray, s: np.ndarray, mu: np.ndarray, var: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean and variance of every machine's power given the aggregate a (T,) and the 0/1 states s (T, n); 0 when OFF."""
    total = np.maximum(s @ var, FLOOR)  # var is floored already: this only guards the rows with every machine OFF
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
        new_mu = np.maximum(mean.sum(axis=0) / count, 0.0)
        var = np.maximum((s * (spread + (mean - new_mu) ** 2)).sum(axis=0) / count, FLOOR)
        converged = np.abs(new_mu - mu).max() < 1e-9
        mu = new_mu
        if converged:
            break
    return mu, var


def patterns(s: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    """Every pattern of ON machines with at least one ON, and its rows."""
    keys, inverse, counts = np.unique(s > 0, axis=0, return_inverse=True, return_counts=True)
    groups = np.split(np.argsort(inverse.ravel(), kind="stable"), np.cumsum(counts)[:-1])
    return [(on, rows) for on, rows in zip(keys, groups, strict=True) if on.any()]


def assignments(on: np.ndarray, mu: np.ndarray, var: np.ndarray, pi: np.ndarray):
    """Every way to draw each ON machine from one of its components. Returns the ON machines (m,), the one-hot
    components (C, m, k), the component means and variances (C, m), and per assignment the variance of the sum and the
    log prior (C,)."""
    # ponytail: k ** m assignments, fine up to about 8 machines ON at once; prune or sample them beyond that
    idx = np.flatnonzero(on)
    z = np.array(list(itertools.product(range(mu.shape[1]), repeat=len(idx))))
    mj, vj = mu[idx, z], var[idx, z]
    return (
        idx,
        z[:, :, None] == np.arange(mu.shape[1]),
        mj,
        vj,
        np.maximum(vj.sum(axis=1), FLOOR),
        np.log(pi[idx, z]).sum(axis=1),
    )


def conditional(a: np.ndarray, mj, vj, v, lp) -> tuple[np.ndarray, np.ndarray]:
    """For rows of one pattern with aggregate a (r,): the posterior weight of every assignment (r, C) and each ON
    machine's mean given the assignment (r, C, m)."""
    r = a[:, None] - mj.sum(axis=1)
    ll = lp - 0.5 * np.log(v) - 0.5 * r**2 / v
    w = np.exp(ll - ll.max(axis=1, keepdims=True))
    return w / w.sum(axis=1, keepdims=True), mj + vj * (r / v)[:, :, None]


def fit_mixture(a: np.ndarray, s: np.ndarray, k: int, iters: int = 300) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """EM for k components per machine: means, variances and weights, (n, k) each. Starts from the single Gaussian of
    `fit`, the components spread from one sd below its mean to one above; k = 1 is `fit`."""
    mu1, var1 = fit(a, s)
    if k == 1:
        return mu1[:, None], var1[:, None], np.ones((len(mu1), 1))
    mu = np.maximum(mu1[:, None] + np.sqrt(var1)[:, None] * np.linspace(-1, 1, k), 0.0)
    var = np.repeat(np.maximum(var1 / k**2, FLOOR)[:, None], k, axis=1)
    pi = np.full(mu.shape, 1 / k)
    groups = patterns(s)
    for _ in range(iters):
        weight, first, second = np.zeros(mu.shape), np.zeros(mu.shape), np.zeros(mu.shape)
        for on, rows in groups:
            idx, onehot, mj, vj, v, lp = assignments(on, mu, var, pi)
            w, mean = conditional(a[rows], mj, vj, v, lp)
            weight[idx] += np.einsum("rc,cmk->mk", w, onehot)
            first[idx] += np.einsum("rc,rcm,cmk->mk", w, mean, onehot)
            second[idx] += np.einsum("rc,rcm,cmk->mk", w, mean**2 + vj - vj**2 / v[:, None], onehot)
        seen = weight > 0  # a machine never ON keeps its start
        new_mu = np.where(seen, np.maximum(first / np.where(seen, weight, 1), 0.0), mu)
        var = np.where(seen, np.maximum(second / np.where(seen, weight, 1) - new_mu**2, FLOOR), var)
        pi = np.maximum(weight / np.maximum(weight.sum(axis=1, keepdims=True), 1e-300), 1e-6)
        pi /= pi.sum(axis=1, keepdims=True)
        converged = np.abs(new_mu - mu).max() < 1e-9
        mu = new_mu
        if converged:
            break
    return mu, var, pi


def estimate(a: np.ndarray, s: np.ndarray, mu: np.ndarray, var: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Posterior mean of every machine's power given the aggregate a (T,) and the 0/1 states s (T, n); 0 when OFF."""
    est = np.zeros(s.shape)
    for on, rows in patterns(s):
        idx, _, mj, vj, v, lp = assignments(on, mu, var, pi)
        for chunk in np.array_split(rows, -(-len(rows) * mj.size // CHUNK)):
            w, mean = conditional(a[chunk], mj, vj, v, lp)
            est[np.ix_(chunk, idx)] = np.einsum("rc,rcm->rm", w, mean)
    return est


def collinear(s: np.ndarray, threshold: float = 0.9) -> list[tuple[int, int]]:
    """Pairs of machines whose on/off states correlate above threshold: the aggregate cannot tell their power apart."""
    with np.errstate(divide="ignore", invalid="ignore"):  # a machine always ON or always OFF has no correlation
        corr = np.atleast_2d(np.corrcoef(s.T))  # a 0-d array for one machine
    return [(int(i), int(j)) for i, j in zip(*np.nonzero(np.triu(corr > threshold, 1)), strict=True)]


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument("--components", type=int, default=3, help="Gaussian components per machine, chosen on October")
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, default=REPO / "results" / "allocation")
    a = p.parse_args(argv)
    if a.components < 1:
        p.error("--components must be at least 1")
    d = a.data_root / a.dataset.upper() / str(a.machines)

    agg = pd.read_csv(d / "aggregate_training.csv", usecols=[0, 1])
    states = pd.read_csv(d / "states_training.csv")
    val = pd.read_csv(d / "aggregate_validation.csv", usecols=[0, 1])
    val_states = pd.read_csv(d / "states_validation.csv")
    for x, y in ((agg, states), (val, val_states)):
        if y.shape[1] - 1 != a.machines or not x.iloc[:, 0].equals(y.iloc[:, 0]):
            raise SystemExit(f"expected {a.machines} machine columns and the aggregate's timestamps in {d}")
    states, val_states = states.iloc[:, 1:].to_numpy(float), val_states.iloc[:, 1:].to_numpy(float)
    power = agg.iloc[:, 1].to_numpy()
    scale = np.abs(power).max() or 1.0

    if pairs := collinear(states):
        print(f"warning: machine pairs {pairs} switch on and off together, so how their power splits is a guess")
    mu, var, pi = fit_mixture(power / scale, states, a.components)
    for j in range(a.machines):
        parts = (
            f"{w:.0%} at {m * scale:.4g} (sd {np.sqrt(v) * scale:.4g})"
            for m, v, w in zip(mu[j], var[j], pi[j], strict=True)
        )
        print(f"machine {j} while ON: {', '.join(parts)}")
    est = np.maximum(estimate(val.iloc[:, 1].to_numpy() / scale, val_states, mu, var, pi), 0.0) * scale

    out = a.results_root / a.dataset.upper() / f"{a.machines}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([val, pd.DataFrame(est, columns=[f"Estimate_{j}" for j in range(a.machines)])], axis=1).to_csv(
        out, index=False
    )
    print(f"saved {out}")


if __name__ == "__main__":
    main()
