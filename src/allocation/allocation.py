"""Gaussian allocation: splits the total power among the ON machines.

- While ON, each machine's power comes from its own mixture of Gaussians ("components"), one per power level, e.g. an
  oven idling or heating. Machines are independent.
- The total (`aggregate` in the files) is the sum over the ON machines.
- EM (expectation-maximisation: alternately estimate each machine's share and refit) fits the components from the
  total and the states alone.
- Each estimate is the machine's posterior mean (expected power given the total), so ON estimates add up to the total.
  A Gaussian allows negative power: those are set to 0 and the others scaled down so they still add up to it.
- --components 1: one Gaussian per machine.
- Trains on the same training rows as the other methods.

Example: python3 src/allocation/allocation.py --dataset hipe --machines 9
"""

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

REPO = Path(__file__).resolve().parents[2]
FLOOR = 1e-6  # minimum variance (total scaled to [0, 1]): keeps the posterior defined when only steady machines run
CHUNK = 2_000_000  # cap on rows x assignments that `conditional` gets at once


def posterior(a: np.ndarray, s: np.ndarray, mu: np.ndarray, var: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Each machine's power mean and variance, given the total a (T,) and 0/1 states s (T, n). Both 0 when OFF."""
    total = np.maximum(s @ var, FLOOR)  # var is already floored; this only guards rows where every machine is OFF
    shift = (a - s @ mu) / total
    return s * (mu + var * shift[:, None]), s * (var - var**2 / total[:, None])


def fit(a: np.ndarray, s: np.ndarray, iters: int = 500) -> tuple[np.ndarray, np.ndarray]:
    """Fit one Gaussian per machine by EM: means and variances (n,). Starts from a non-negative least-squares fit. A
    machine never ON keeps mean 0."""
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
    """Each set of ON machines that occurs (at least one ON), with its rows."""
    keys, inverse, counts = np.unique(s > 0, axis=0, return_inverse=True, return_counts=True)
    groups = np.split(np.argsort(inverse.ravel(), kind="stable"), np.cumsum(counts)[:-1])
    return [(on, rows) for on, rows in zip(keys, groups, strict=True) if on.any()]


def assignments(on: np.ndarray, mu: np.ndarray, var: np.ndarray, pi: np.ndarray):
    """Every way to pick one component per ON machine (C "assignments").

    Returns the ON machines (m,), the picks one-hot (C, m, k), their means and variances (C, m), and per assignment the
    variance of the sum and the log prior, i.e. the log of the picked weights' product (C,)."""
    # ponytail: tries every combination of the ON machines' components; fine up to about 3 ** 8, prune or sample beyond
    idx = np.flatnonzero(on)
    z = np.array(list(itertools.product(*(range(np.count_nonzero(pi[i])) for i in idx))))
    mj, vj = mu[idx, z], var[idx, z]
    return (
        idx,
        z[:, :, None] == np.arange(mu.shape[1]),
        mj,
        vj,
        np.maximum(vj.sum(axis=1), FLOOR),
        np.log(pi[idx, z]).sum(axis=1),
    )


def conditional(a: np.ndarray, mj, v, lp) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For the rows of one pattern, with total a (r,), return:
    - each assignment's posterior weight (r, C)
    - q (r, C): ON machine j's mean under an assignment is mj + vj * q, kept apart so no (r, C, m) array is built
    - the log-likelihood of each row's total (r,)"""
    r = a[:, None] - mj.sum(axis=1)
    ll = lp - 0.5 * np.log(2 * np.pi * v) - 0.5 * r**2 / v
    top = ll.max(axis=1, keepdims=True)
    w = np.exp(ll - top)
    total = w.sum(axis=1, keepdims=True)
    return w / total, r / v, (top + np.log(total))[:, 0]


def chunks(rows: np.ndarray, c: int) -> list[np.ndarray]:
    """rows in pieces of at most CHUNK // c, c being the number of assignments."""
    return np.array_split(rows, -(-len(rows) * c // CHUNK))


def fit_mixture(
    a: np.ndarray, s: np.ndarray, k: int = 1, iters: int = 300
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit k components per machine by EM.

    Returns means, variances and weights, each (n, k). Starts from `fit`'s single Gaussian, spreading each machine's
    components evenly from one sd below its mean to one above. k = 1 is just `fit`."""
    mu1, var1 = fit(a, s)
    if k == 1:
        return mu1[:, None], var1[:, None], np.ones((len(mu1), 1))
    mu = np.maximum(mu1[:, None] + np.sqrt(var1)[:, None] * (2 * np.arange(k) / (k - 1) - 1), 0.0)
    var = np.repeat(np.maximum(var1 / k**2, FLOOR)[:, None], k, axis=1)
    pi = np.full(mu.shape, 1 / k)
    groups = patterns(s)
    for _ in range(iters):
        weight, first, second = np.zeros(mu.shape), np.zeros(mu.shape), np.zeros(mu.shape)
        for on, rows in groups:
            idx, onehot, mj, vj, v, lp = assignments(on, mu, var, pi)
            s0 = s1 = s2 = 0.0  # per assignment, over the rows: sums of w, w * q and w * q ** 2
            for chunk in chunks(rows, len(lp)):
                w, q, _ = conditional(a[chunk], mj, v, lp)
                s0, s1, s2 = s0 + w.sum(axis=0), s1 + (w * q).sum(axis=0), s2 + (w * q**2).sum(axis=0)
            s0, s1, s2 = s0[:, None], s1[:, None], s2[:, None]
            # sums of w * mean and w * (mean ** 2 + its variance), with mean = mj + vj * q
            weight[idx] += np.einsum("c,cmk->mk", s0[:, 0], onehot)
            first[idx] += np.einsum("cm,cmk->mk", mj * s0 + vj * s1, onehot)
            moment = mj**2 * s0 + 2 * mj * vj * s1 + vj**2 * s2 + (vj - vj**2 / v[:, None]) * s0
            second[idx] += np.einsum("cm,cmk->mk", moment, onehot)
        seen = weight > 0  # zero weight (machine never ON): keep the start
        new_mu = np.where(seen, np.maximum(first / np.where(seen, weight, 1), 0.0), mu)
        var = np.where(seen, np.maximum(second / np.where(seen, weight, 1) - new_mu**2, FLOOR), var)
        # floored: `assignments` counts components by nonzero weight
        pi = np.maximum(weight / np.maximum(weight.sum(axis=1, keepdims=True), 1e-300), 1e-6)
        pi /= pi.sum(axis=1, keepdims=True)
        converged = np.abs(new_mu - mu).max() < 1e-9
        mu = new_mu
        if converged:
            break
    return mu, var, pi


def estimate(a: np.ndarray, s: np.ndarray, mu: np.ndarray, var: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Posterior mean of each machine's power, given the total a (T,) and the 0/1 states s (T, n). 0 when OFF."""
    est = np.zeros(s.shape)
    for on, rows in patterns(s):
        idx, _, mj, vj, v, lp = assignments(on, mu, var, pi)
        for chunk in chunks(rows, len(lp)):
            w, q, _ = conditional(a[chunk], mj, v, lp)
            est[np.ix_(chunk, idx)] = w @ mj + (w * q) @ vj
    return est


def collinear(s: np.ndarray, threshold: float = 0.9) -> list[tuple[int, int]]:
    """Pairs of machines whose on/off states correlate above `threshold`: the total can't tell their power apart."""
    with np.errstate(divide="ignore", invalid="ignore"):  # a machine always ON or always OFF has no correlation (NaN)
        corr = np.atleast_2d(np.corrcoef(s.T))  # np.corrcoef gives a 0-d array for one machine
    return [(int(i), int(j)) for i, j in zip(*np.nonzero(np.triu(corr > threshold, 1)), strict=True)]


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", choices=["hipe", "imdeld"], required=True)
    p.add_argument("--machines", type=int, required=True)
    p.add_argument(
        "--components",
        type=int,
        default=3,
        help="Gaussian components per machine, chosen on October",
    )
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
            if w > 0
        )
        print(f"machine {j} while ON: {', '.join(parts)}")
    a_val = val.iloc[:, 1].to_numpy()[:, None]
    est = np.maximum(estimate(a_val[:, 0] / scale, val_states, mu, var, pi), 0.0)
    total = est.sum(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):  # no machine ON: 0 / 0 = NaN, set to 0
        shares = np.where(total > 0, est / total, val_states / val_states.sum(axis=1, keepdims=True))
    est = np.nan_to_num(shares * a_val)

    out = a.results_root / a.dataset.upper() / f"{a.machines}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([val, pd.DataFrame(est, columns=[f"Estimate_{j}" for j in range(a.machines)])], axis=1).to_csv(
        out, index=False
    )
    print(f"saved {out}")


if __name__ == "__main__":
    main()
