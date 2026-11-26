"""Gaussian allocation: splits the total power among the ON machines.

- While ON, each machine's power comes from its own mixture of Gaussians ("components"), one per power level, e.g. an
  oven idling or heating. Machines are independent.
- The total (`aggregate` in the files) is the sum over the ON machines.
- --phases (HIPE): the total is instead the meter's 6 per-phase readings, active and reactive power on each phase
  (`phases` in the files), and each component is a Gaussian over those 6. Machines on other phases, or with other
  reactive power, then look different in the total. Writes to results/allocation_phases, beside the total-only run.
- EM (expectation-maximisation: alternately estimate each machine's share and refit) fits the components from the
  total and the states alone.
- Each estimate is the machine's posterior mean active power (expected power given the total), so ON estimates add up
  to the total. A Gaussian allows negative power: those are set to 0 and the others scaled so they add up to it.
- --components 1: one Gaussian per machine.
- Trains on the same training rows as the other methods.

Example: python3 src/allocation/allocation.py --dataset hipe --machines 9 --phases
"""

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

REPO = Path(__file__).resolve().parents[2]
FLOOR = (
    1e-6  # minimum variance (each reading scaled to [-1, 1]): keeps the posterior defined when only steady machines run
)
CHUNK = 2_000_000  # cap on rows x assignments x readings that `conditional` gets at once
PHASES = ["P1_kW", "P2_kW", "P3_kW", "Q1_kvar", "Q2_kvar", "Q3_kvar"]  # columns of the phases files


def floor_cov(c: np.ndarray) -> np.ndarray:
    """Covariances (..., d, d), made symmetric with every eigenvalue at least FLOOR."""
    lam, v = np.linalg.eigh((c + np.swapaxes(c, -1, -2)) / 2)
    return (v * np.maximum(lam, FLOOR)[..., None, :]) @ np.swapaxes(v, -1, -2)


def patterns(s: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    """Each set of ON machines that occurs (at least one ON), with its rows."""
    keys, inverse, counts = np.unique(s > 0, axis=0, return_inverse=True, return_counts=True)
    groups = np.split(np.argsort(inverse.ravel(), kind="stable"), np.cumsum(counts)[:-1])
    return [(on, rows) for on, rows in zip(keys, groups, strict=True) if on.any()]


def assignments(on: np.ndarray, mu: np.ndarray, cov: np.ndarray, pi: np.ndarray):
    """Every way to pick one component per ON machine (C "assignments").

    mu (n, k, d), cov (n, k, d, d), pi (n, k). Returns the ON machines (m,), the picks one-hot (C, m, k), their means
    (C, m, d) and covariances (C, m, d, d), and per assignment the total's mean (C, d), the inverse of its covariance
    (C, d, d), the log of that covariance's determinant and the log prior, i.e. the log of the picked weights' product
    (C,)."""
    # ponytail: tries every combination of the ON machines' components; fine up to about 3 ** 10, prune or sample beyond
    idx = np.flatnonzero(on)
    z = np.array(list(itertools.product(*(range(np.count_nonzero(pi[i])) for i in idx))))
    mj, cj = mu[idx, z], cov[idx, z]
    total = cj.sum(axis=1)
    return (
        idx,
        z[:, :, None] == np.arange(mu.shape[1]),
        mj,
        cj,
        mj.sum(axis=1),
        np.linalg.inv(total),
        np.linalg.slogdet(total)[1],
        np.log(pi[idx, z]).sum(axis=1),
    )


def conditional(y: np.ndarray, m, g, logdet, lp) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For the rows of one pattern, with totals y (r, d), return:
    - each assignment's posterior weight (r, C)
    - q (r, C, d): ON machine j's mean under an assignment is mj + cj q, kept apart so no (r, C, m, d) array is built
    - the log-likelihood of each row's total (r,)"""
    r = y[:, None, :] - m
    q = np.einsum("cde,rce->rcd", g, r)
    ll = lp - 0.5 * (y.shape[1] * np.log(2 * np.pi) + logdet) - 0.5 * (r * q).sum(axis=2)
    top = ll.max(axis=1, keepdims=True)
    w = np.exp(ll - top)
    total = w.sum(axis=1, keepdims=True)
    return w / total, q, (top + np.log(total))[:, 0]


def chunks(rows: np.ndarray, c: int) -> list[np.ndarray]:
    """rows in pieces of at most CHUNK // c, c being the number of assignments times readings."""
    return np.array_split(rows, -(-len(rows) * c // CHUNK))


def em(y, s, model, nonneg, iters):
    """EM from the given start, model = means (n, k, d), covariances (n, k, d, d) and weights (n, k). A machine never ON
    keeps its start."""
    mu, cov, pi = model
    groups = patterns(s)
    for _ in range(iters):
        weight, first, second = np.zeros(pi.shape), np.zeros(mu.shape), np.zeros(cov.shape)
        for on, rows in groups:
            idx, onehot, mj, cj, m, g, logdet, lp = assignments(on, mu, cov, pi)
            s0 = s1 = s2 = 0.0  # per assignment, over the rows: sums of w, w * q and w * q q'
            for chunk in chunks(rows, len(lp) * y.shape[1]):
                w, q, _ = conditional(y[chunk], m, g, logdet, lp)
                s0 = s0 + w.sum(axis=0)
                s1 = s1 + np.einsum("rc,rcd->cd", w, q)
                s2 = s2 + np.einsum("rc,rcd,rce->cde", w, q, q)
            # sums of w * mean and w * (mean mean' + its covariance), with mean = mj + cj q
            cs1 = np.einsum("cmde,ce->cmd", cj, s1)
            cg = np.einsum("cmde,cef->cmdf", cj, g)
            outer = mj[..., :, None] * mj[..., None, :] + cj - np.einsum("cmde,cmfe->cmdf", cg, cj)
            moment = (
                s0[:, None, None, None] * outer
                + mj[..., :, None] * cs1[..., None, :]
                + cs1[..., :, None] * mj[..., None, :]
                + np.einsum("cmde,cef,cmgf->cmdg", cj, s2, cj)
            )
            weight[idx] += np.einsum("c,cmk->mk", s0, onehot)
            first[idx] += np.einsum("cmd,cmk->mkd", mj * s0[:, None, None] + cs1, onehot)
            second[idx] += np.einsum("cmde,cmk->mkde", moment, onehot)
        seen = weight > 0  # zero weight (machine never ON): keep the start
        w = np.where(seen, weight, 1)
        new_mu = np.where(seen[..., None], first / w[..., None], mu)
        new_mu[..., nonneg] = np.maximum(new_mu[..., nonneg], 0.0)
        c = second / w[..., None, None] - new_mu[..., :, None] * new_mu[..., None, :]
        cov = np.where(seen[..., None, None], floor_cov(c), cov)
        # floored: `assignments` counts components by nonzero weight
        pi = np.maximum(weight / np.maximum(weight.sum(axis=1, keepdims=True), 1e-300), 1e-6)
        pi /= pi.sum(axis=1, keepdims=True)
        converged = np.abs(new_mu - mu).max() < 1e-9
        mu = new_mu
        if converged:
            break
    return mu, cov, pi


def fit_mixture(
    y: np.ndarray, s: np.ndarray, k: int, e: np.ndarray, nonneg: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit k components per machine by EM, from the totals y (T, d) and the 0/1 states s (T, n).

    e (d,): weights that turn the readings into active power. nonneg (d,): readings that can't be negative, whose means
    are kept at 0 or above. Returns means (n, k, d), covariances (n, k, d, d) and weights (n, k).

    First one Gaussian per machine, from a least-squares start. Then each machine's k components are spread evenly
    along active power, from one sd below its mean to one above."""
    on = s.any(axis=1)
    y, s = y[on], s[on]
    n, d = s.shape[1], y.shape[1]
    mu, cov = np.zeros((n, 1, d)), np.zeros((n, 1, d, d))
    for i in range(d):
        m = nnls(s, y[:, i])[0] if nonneg[i] else np.linalg.lstsq(s, y[:, i], rcond=None)[0]
        mu[:, 0, i], cov[:, 0, i, i] = m, nnls(s, (y[:, i] - s @ m) ** 2)[0] + FLOOR
    mu, cov, pi = em(y, s, (mu, cov, np.ones((n, 1))), nonneg, 500)
    if k == 1:
        return mu, cov, pi
    step = cov[:, 0] @ e / np.sqrt(e @ cov[:, 0] @ e)[:, None]  # 1 sd along active power, per machine (n, d)
    mu = mu + (2 * np.arange(k) / (k - 1) - 1)[None, :, None] * step[:, None, :]
    mu[..., nonneg] = np.maximum(mu[..., nonneg], 0.0)
    cov = np.repeat(floor_cov(cov[:, 0] / k**2)[:, None], k, axis=1)
    return em(y, s, (mu, cov, np.full((n, k), 1 / k)), nonneg, 300)


def estimate(y: np.ndarray, s: np.ndarray, model, e: np.ndarray) -> np.ndarray:
    """Posterior mean active power (e . readings) of each machine, given the totals y (T, d), the 0/1 states s (T, n)
    and the fitted model (means, covariances, weights). 0 when OFF."""
    mu, cov, pi = model
    est = np.zeros(s.shape)
    for on, rows in patterns(s):
        idx, _, mj, cj, m, g, logdet, lp = assignments(on, mu, cov, pi)
        ce = np.einsum("cmde,d->cem", cj, e)
        for chunk in chunks(rows, len(lp) * y.shape[1]):
            w, q, _ = conditional(y[chunk], m, g, logdet, lp)
            est[np.ix_(chunk, idx)] = w @ (mj @ e) + np.einsum("rc,rcd,cdm->rm", w, q, ce)
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
    p.add_argument("--phases", action="store_true", help="split the per-phase readings (HIPE only)")
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, help="default: results/allocation, or results/allocation_phases")
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
    if a.phases:
        if not (d / "phases_training.csv").exists():
            raise SystemExit(f"no phases_training.csv in {d}: --phases needs HIPE, made by hipe.py")
        readings = [pd.read_csv(d / f"phases_{split}.csv") for split in ("training", "validation")]
        if not all(r.iloc[:, 0].equals(x.iloc[:, 0]) for r, x in zip(readings, (agg, val), strict=True)):
            raise SystemExit(f"the phases files' timestamps differ from the aggregate's in {d}")
        y, y_val = (r[PHASES].to_numpy() for r in readings)
        e, nonneg = np.array([1.0, 1, 1, 0, 0, 0]), np.zeros(6, bool)  # per-phase power can be negative
    else:
        y, y_val = agg.iloc[:, 1:2].to_numpy(), val.iloc[:, 1:2].to_numpy()
        e, nonneg = np.ones(1), np.ones(1, bool)
    scale = np.abs(y).max(axis=0)
    scale[scale == 0] = 1.0
    e = e * scale  # active power from the scaled readings

    if pairs := collinear(states):
        print(f"warning: machine pairs {pairs} switch on and off together, so how their power splits is a guess")
    model = mu, cov, pi = fit_mixture(y / scale, states, a.components, e, nonneg)
    for j in range(a.machines):
        parts = (
            f"{w:.0%} at {m @ e:.4g} (sd {np.sqrt(e @ c @ e):.4g})"
            for m, c, w in zip(mu[j], cov[j], pi[j], strict=True)
            if w > 0
        )
        print(f"machine {j} while ON: {', '.join(parts)}")
    a_val = val.iloc[:, 1].to_numpy()[:, None]
    est = np.maximum(estimate(y_val / scale, val_states, model, e), 0.0)
    total = est.sum(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):  # no machine ON: 0 / 0 = NaN, set to 0
        shares = np.where(total > 0, est / total, val_states / val_states.sum(axis=1, keepdims=True))
    est = np.nan_to_num(shares * a_val)

    root = a.results_root or REPO / "results" / ("allocation_phases" if a.phases else "allocation")
    out = root / a.dataset.upper() / f"{a.machines}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([val, pd.DataFrame(est, columns=[f"Estimate_{j}" for j in range(a.machines)])], axis=1).to_csv(
        out, index=False
    )
    print(f"saved {out}")


if __name__ == "__main__":
    main()
