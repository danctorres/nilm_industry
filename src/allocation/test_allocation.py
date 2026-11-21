"""Self-check of the Gaussian allocation: python3 src/allocation/test_allocation.py"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from allocation import fit, main, posterior

# three machines with known means and spreads: EM recovers them from the aggregate and states alone
rng = np.random.default_rng(0)
mu, sd = np.array([0.3, 0.1, 0.5]), np.array([0.01, 0.005, 0.1])
s = (rng.random((20000, 3)) < 0.5).astype(float)
p = s * rng.normal(mu, sd, (20000, 3))
a = p.sum(axis=1)
fit_mu, fit_var = fit(a, s)
assert np.allclose(fit_mu, mu, rtol=0.01), fit_mu
assert np.allclose(np.sqrt(fit_var), sd, rtol=0.1), np.sqrt(fit_var)

# the ON estimates add up to the aggregate, OFF machines are 0, and the steady machines keep their mean
est = posterior(a, s, fit_mu, fit_var)[0]
assert np.allclose(est.sum(axis=1), a, atol=1e-3) and (est[s == 0] == 0).all()
assert np.abs(est - p).mean() < 0.5 * np.abs(s * fit_mu - p).mean()

# end to end: trains on the unsplit rows outside the validation split, estimates the validation rows
with tempfile.TemporaryDirectory() as name:
    d = Path(name) / "HIPE" / "3"
    d.mkdir(parents=True)
    ts = pd.date_range("2017-10-23", periods=len(a), freq="s").strftime("%d-%b-%Y %H:%M:%S")
    cols = {f"Eq{j}_State": s[:, j].astype(int) for j in range(3)}
    pd.DataFrame({"timestamp": ts, "active_power": a}).to_csv(d / "aggregate.csv", index=False)
    pd.DataFrame({"timestamp": ts, **cols}).to_csv(d / "states.csv", index=False)
    pd.DataFrame({"timestamp": ts[:100], "active_power": a[:100]}).to_csv(d / "aggregate_validation.csv", index=False)
    pd.DataFrame({"timestamp": ts, **cols}).iloc[:100].to_csv(d / "states_validation.csv", index=False)
    main(["--dataset", "hipe", "--machines", "3", "--data-root", name, "--results-root", name])
    out = pd.read_csv(Path(name) / "HIPE" / "3.csv")
    assert list(out.columns) == ["timestamp", "active_power", "Estimate_0", "Estimate_1", "Estimate_2"]
    assert list(out.timestamp) == list(ts[:100]) and np.abs(out.iloc[:, 2:].to_numpy() - p[:100]).mean() < 0.02

print("ok")
