"""Self-check of the Gaussian allocation: python3 src/allocation/test_allocation.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from allocation import PHASES, collinear, estimate, fit_mixture, main

ONE, YES = np.ones(1), np.ones(1, bool)  # one reading, active power, which can't be negative

# three machines with known means and spreads: EM recovers them from the total and states alone
rng = np.random.default_rng(0)
mu, sd = np.array([0.3, 0.1, 0.5]), np.array([0.01, 0.005, 0.1])
s = (rng.random((20000, 3)) < 0.5).astype(float)
p = s * rng.normal(mu, sd, (20000, 3))
a = p.sum(axis=1)
fit_mu, fit_cov, fit_pi = fit_mixture(a[:, None], s, 1, ONE, YES)
assert np.allclose(fit_mu[:, 0, 0], mu, rtol=0.01), fit_mu
assert np.allclose(np.sqrt(fit_cov[:, 0, 0, 0]), sd, rtol=0.1), fit_cov
assert (fit_pi == 1).all()

# independent machines raise no warning; a machine that copies another's states does
assert collinear(s) == [] and collinear(np.c_[s, s[:, 1]]) == [(1, 3)] and collinear(s[:, :1]) == []

# the ON estimates add up to the total, OFF machines are 0, and the error is under half that of guessing the means
est = estimate(a[:, None], s, (fit_mu, fit_cov, fit_pi), ONE)
assert np.allclose(est.sum(axis=1), a, atol=1e-3) and (est[s == 0] == 0).all()
assert np.abs(est - p).mean() < 0.5 * np.abs(s * fit_mu[:, 0, 0] - p).mean()
# exactly, even beside a machine at the variance floor, which stays at its mean while the other takes the rest
steady_and_wide = np.array([[[0.3]], [[0.5]]]), np.array([[[[1e-6]]], [[[0.01]]]]), np.ones((2, 1))
two = estimate(np.ones((1, 1)), np.ones((1, 2)), steady_and_wide, ONE)
assert np.isclose(two.sum(), 1.0, rtol=0, atol=1e-12) and abs(two[0, 0] - 0.3) < 1e-4, two

# a machine that idles at 0.1 or heats at 4, plus two steady ones. EM finds both levels from the total alone, and
# the mixture splits the total far better than one Gaussian
heat = rng.random(len(a)) < 0.3
p2 = (
    s
    * np.c_[
        np.where(heat, rng.normal(4, 0.2, len(a)), rng.normal(0.1, 0.01, len(a))),
        rng.normal(mu[1:], sd[1:], (len(a), 2)),
    ]
)
a2 = p2.sum(axis=1)
mix = fit_mixture(a2[:, None], s, 2, ONE, YES)
levels = np.sort(mix[0][0, :, 0])
assert np.allclose(levels, [0.1, 4], rtol=0.05) and np.isclose(mix[2][0, np.argmax(mix[0][0, :, 0])], 0.3, atol=0.02)
est2 = estimate(a2[:, None], s, mix, ONE)
assert np.allclose(est2.sum(axis=1), a2, atol=1e-3) and (est2[s == 0] == 0).all()
mixed = np.abs(est2 - p2).mean()
single = np.abs(estimate(a2[:, None], s, fit_mixture(a2[:, None], s, 1, ONE, YES), ONE) - p2).mean()
assert mixed < 0.5 * single, (mixed, single)

# per-phase readings: two machines that draw the same, widely varying power, one on phase 1 and one on phase 2, and a
# steady one spread over all three. The active total can't tell the first two apart; the phases can
p3 = s * np.c_[rng.normal(2, 0.5, (len(a), 2)), rng.normal(0.6, 0.01, len(a))]
y = np.zeros((len(a), 6))
y[:, :3] = p3[:, :1] * [1, 0, 0] + p3[:, 1:2] * [0, 1, 0] + p3[:, 2:] / 3
y[:, 3] = 0.4 * p3[:, 0]  # reactive power on phase 1 only
a3, e = y[:, :3].sum(axis=1), np.array([1.0, 1, 1, 0, 0, 0])
phases = estimate(y, s, fit_mixture(y, s, 1, e, np.zeros(6, bool)), e)
total_only = estimate(a3[:, None], s, fit_mixture(a3[:, None], s, 1, ONE, YES), ONE)
assert np.allclose(phases.sum(axis=1), a3, atol=1e-3) and (phases[s == 0] == 0).all()
assert np.abs(phases - p3).mean() < 0.1 * np.abs(total_only - p3).mean(), (phases, total_only)

# end to end: trains on the training rows, estimates the validation rows, from the total or from the phases
with tempfile.TemporaryDirectory() as name:
    d = Path(name) / "HIPE" / "3"
    d.mkdir(parents=True)
    ts = pd.date_range("2017-10-23", periods=len(a), freq="s").strftime("%d-%b-%Y %H:%M:%S")
    cols = {f"Eq{j}_State": s[:, j].astype(int) for j in range(3)}
    for split, rows in (("training", slice(100, None)), ("validation", slice(100))):
        pd.DataFrame({"timestamp": ts, "active_power": a3})[rows].to_csv(d / f"aggregate_{split}.csv", index=False)
        pd.DataFrame({"timestamp": ts, **cols})[rows].to_csv(d / f"states_{split}.csv", index=False)
        pd.DataFrame({"timestamp": ts, **dict(zip(PHASES, y.T, strict=True))})[rows].to_csv(
            d / f"phases_{split}.csv", index=False
        )
    errors = {}
    for extra in ([], ["--phases"]):
        args = [
            "--dataset",
            "hipe",
            "--machines",
            "3",
            "--components",
            "1",
            "--data-root",
            name,
            "--results-root",
            name,
        ]
        main(args + extra)
        out = pd.read_csv(Path(name) / "HIPE" / "3.csv")
        assert list(out.columns) == ["timestamp", "active_power", "Estimate_0", "Estimate_1", "Estimate_2"]
        assert list(out.timestamp) == list(ts[:100])
        assert np.allclose(out.iloc[:, 2:].sum(axis=1), out.active_power) and (out.iloc[:, 2:] >= 0).all().all()
        errors[bool(extra)] = np.abs(out.iloc[:, 2:].to_numpy() - p3[:100]).mean()
    assert errors[True] < 0.1 * errors[False], errors

print("ok")
