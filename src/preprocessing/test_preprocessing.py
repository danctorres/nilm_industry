"""Self-check of the preprocessing: python3 src/preprocessing/test_preprocessing.py"""

import numpy as np
import pandas as pd
from common import matlab_round, movmean, seconds, spline, split_train_validation

# movmean: the example from the MATLAB documentation, an even window, and a window longer than the data
a = [4, 8, 6, -1, -2, -3, -1, 3, 4, 5]
assert np.allclose(movmean(a, 3), [6, 6, 13 / 3, 1, -2, -2, -1 / 3, 2, 4, 4.5])
assert np.allclose(movmean([1, 2, 3, 4, 5], 4), [1.5, 2, 2.5, 3.5, 4])
assert np.allclose(movmean([1, 2, 3], 10), [2, 2, 2])

# spline: not-a-knot reproduces a cubic exactly, inside and outside the data
x = np.array([0.0, 1.0, 2.5, 3.0, 5.0])
assert np.allclose(spline(x, x**3 - 2 * x, [0.5, 4.0, 6.0]), [0.125 - 1, 64 - 8, 216 - 12])

# matlab_round: halves away from zero
assert list(matlab_round(np.array([0.5, 1.5, 2.5, -2.5]))) == [1, 2, 3, -3]

assert list(seconds(pd.Series(pd.to_datetime(["1970-01-01 00:00:01", "2018-02-21 00:00:00"])))) == [1, 1519171200]

# split: whole blocks minus their edges for validation, training at least 2 * gap away from them, the same number of
# rows from every kept bin of the other blocks, reproducible
t = np.arange(20000.0)
agg = np.random.default_rng(5).normal(100, 10, len(t))
tr, val = split_train_validation(t, agg, 1000, 50, np.random.default_rng(1))
tr2, val2 = split_train_validation(t, agg, 1000, 50, np.random.default_rng(1))
assert np.array_equal(tr, tr2) and np.array_equal(val, val2)
assert len(val) == 6 * 900 and np.array_equal(val, np.sort(val))  # 6 of 20 blocks, 50 s off each edge
assert np.abs(t[tr][:, None] - t[val][None, :]).min() >= 100
others = ~np.isin(t // 1000, t[val] // 1000) & (t % 1000 >= 50) & (t % 1000 < 950)
counts, edges = np.histogram(agg[others], agg[others].mean() + np.arange(-3, 4) * agg[others].std(ddof=1))
assert list(np.histogram(agg[tr], edges)[0]) == [min(490, counts[counts > 100].min()) * (c > 100) for c in counts]

print("ok")
