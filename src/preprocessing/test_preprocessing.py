"""Self-check of common.py's seconds and split: python3 src/preprocessing/test_preprocessing.py"""

import numpy as np
import pandas as pd
from common import seconds, split_train_validation

assert list(seconds(pd.Series(pd.to_datetime(["1970-01-01 00:00:01", "2018-02-21 00:00:00"])))) == [1, 1519171200]

# split: test = whole blocks minus their edges; training = at least 2 * gap away, the same number from every kept
# bin of the other blocks; reproducible
t = np.arange(20000.0)
agg = np.random.default_rng(5).normal(100, 10, len(t))
tr, val = split_train_validation(t, agg, 1000, 50, np.random.default_rng(1))
tr2, val2 = split_train_validation(t, agg, 1000, 50, np.random.default_rng(1))
assert np.array_equal(tr, tr2) and np.array_equal(val, val2)
assert len(val) == 6 * 900 and np.array_equal(val, np.sort(val))  # 6 of 20 blocks, 50 s off each edge
assert np.abs(t[tr][:, None] - t[val][None, :]).min() >= 100
others = ~np.isin(t // 1000, t[val] // 1000) & (t % 1000 >= 50) & (t % 1000 < 950)
edges = agg[others].mean() + np.arange(-2, 3) * agg[others].std(ddof=1)  # the outer bins are open-ended
counts, per_bin = (np.bincount(np.searchsorted(edges, x, side="right"), minlength=6) for x in (agg[others], agg[tr]))
assert list(per_bin) == [min(490, counts[counts > 100].min()) * (c > 100) for c in counts]
assert agg[tr].max() > agg[others].mean() + 3 * agg[others].std(ddof=1)  # the peaks are drawn too

print("ok")
