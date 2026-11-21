"""Self-check of the Gaussian allocation: python3 src/allocation/test_allocation.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from allocation import collinear, fit, main, posterior

# three machines with known means and spreads: EM recovers them from the aggregate and states alone
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

# the ON estimates add up to the aggregate, OFF machines are 0, and the steady machines keep their mean
est = posterior(a, s, fit_mu, fit_var)[0]
assert np.allclose(est.sum(axis=1), a, atol=1e-3) and (est[s == 0] == 0).all()
# exactly, even for a machine at the variance floor
one = posterior(np.array([0.31]), np.array([[1.0]]), np.array([0.3]), np.array([1e-6]))[0]
assert np.isclose(one.item(), 0.31, rtol=0, atol=1e-12), one
assert np.abs(est - p).mean() < 0.5 * np.abs(s * fit_mu - p).mean()

# end to end: trains on the training split, estimates the validation rows
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
