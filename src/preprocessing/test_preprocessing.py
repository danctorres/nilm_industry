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

# split: per kept bin floor(n_bin * 0.7) training and floor(n_bin * 0.3) validation, disjoint, reproducible
agg = np.random.default_rng(5).normal(100, 10, 5000)
tr, val = split_train_validation(agg, 0.7, np.random.default_rng(1))
tr2, val2 = split_train_validation(agg, 0.7, np.random.default_rng(1))
assert np.array_equal(tr, tr2) and np.array_equal(val, val2)
assert not set(tr) & set(val)
counts, _ = np.histogram(agg, agg.mean() + np.arange(-3, 4) * agg.std(ddof=1))
kept = counts[counts > 100]
n_bin = min(700, kept.min())
assert len(tr) == len(kept) * int(np.floor(n_bin * 0.7)) and len(val) == len(kept) * int(np.floor(n_bin * 0.3))

print("ok")
