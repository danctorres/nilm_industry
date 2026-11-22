"""Self-check of the Gaussian allocation: python3 src/allocation/test_allocation.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from allocation import collinear, estimate, fit, fit_mixture, main, posterior, select

# three machines with known means and spreads: EM recovers them from the total and states alone
rng = np.random.default_rng(0)
mu, sd = np.array([0.3, 0.1, 0.5]), np.array([0.01, 0.005, 0.1])
s = (rng.random((20000, 3)) < 0.5).astype(float)
p = s * rng.normal(mu, sd, (20000, 3))
a = p.sum(axis=1)
fit_mu, fit_var = fit(a, s)
assert np.allclose(fit_mu, mu, rtol=0.01), fit_mu
assert np.allclose(np.sqrt(fit_var), sd, rtol=0.1), np.sqrt(fit_var)

# independent machines raise no warning; a machine that copies another's states does
assert collinear(s) == [] and collinear(np.c_[s, s[:, 1]]) == [(1, 3)] and collinear(s[:, :1]) == []

# the ON estimates add up to the total, OFF machines are 0, and the error is under half that of guessing the means
est = posterior(a, s, fit_mu, fit_var)[0]
assert np.allclose(est.sum(axis=1), a, atol=1e-3) and (est[s == 0] == 0).all()
# exactly, even for a machine at the variance floor
one = posterior(np.array([0.31]), np.array([[1.0]]), np.array([0.3]), np.array([1e-6]))[0]
assert np.isclose(one.item(), 0.31, rtol=0, atol=1e-12), one
assert np.abs(est - p).mean() < 0.5 * np.abs(s * fit_mu - p).mean()

# one component per machine gives exactly the single-Gaussian fit
mix_mu, mix_var, mix_pi = fit_mixture(a, s, 1)
assert np.array_equal(mix_mu[:, 0], fit_mu) and np.array_equal(mix_var[:, 0], fit_var) and (mix_pi == 1).all()
assert np.allclose(estimate(a, s, mix_mu, mix_var, mix_pi), est, rtol=0, atol=1e-12)

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
mix_mu, mix_var, mix_pi = fit_mixture(a2, s, 2)
levels = np.sort(mix_mu[0])
assert np.allclose(levels, [0.1, 4], rtol=0.05) and np.isclose(mix_pi[0, np.argmax(mix_mu[0])], 0.3, atol=0.02), mix_mu
est2 = estimate(a2, s, mix_mu, mix_var, mix_pi)
assert np.allclose(est2.sum(axis=1), a2, atol=1e-3) and (est2[s == 0] == 0).all()
mixed = np.abs(est2 - p2).mean()
single = np.abs(posterior(a2, s, *fit(a2, s))[0] - p2).mean()
assert mixed < 0.5 * single, (mixed, single)

# BIC picks two levels for the heating machine and one for each steady one
k, (sel_mu, _, sel_pi) = select(a2[:5000], s[:5000])
assert list(k) == [2, 1, 1] and (sel_pi[1:, 1:] == 0).all(), k
assert np.allclose(np.sort(sel_mu[0]), [0.1, 4], rtol=0.05), sel_mu

# end to end: trains on the training rows, estimates the validation rows
with tempfile.TemporaryDirectory() as name:
    d = Path(name) / "HIPE" / "3"
    d.mkdir(parents=True)
    ts = pd.date_range("2017-10-23", periods=len(a), freq="s").strftime("%d-%b-%Y %H:%M:%S")
    cols = {f"Eq{j}_State": s[:, j].astype(int) for j in range(3)}
    for split, rows in (("training", slice(100, None)), ("validation", slice(100))):
        pd.DataFrame({"timestamp": ts, "active_power": a})[rows].to_csv(d / f"aggregate_{split}.csv", index=False)
        pd.DataFrame({"timestamp": ts, **cols})[rows].to_csv(d / f"states_{split}.csv", index=False)
    main(["--dataset", "hipe", "--machines", "3", "--data-root", name, "--results-root", name])
    out = pd.read_csv(Path(name) / "HIPE" / "3.csv")
    assert list(out.columns) == ["timestamp", "active_power", "Estimate_0", "Estimate_1", "Estimate_2"]
    assert list(out.timestamp) == list(ts[:100]) and np.abs(out.iloc[:, 2:].to_numpy() - p[:100]).mean() < 0.02

print("ok")
