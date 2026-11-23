"""Self-check of common.py's seconds and split: python3 src/preprocessing/test_preprocessing.py"""

import numpy as np
import pandas as pd
from common import TRAINING_ROWS, draw_training, seconds, split_train_validation

assert list(seconds(pd.Series(pd.to_datetime(["1970-01-01 00:00:01", "2018-02-21 00:00:00"])))) == [1, 1519171200]

# split: test = whole blocks minus their edges; training = at least 2 * gap away, every row of the other blocks
# (fewer than TRAINING_ROWS here) in random order; reproducible
t = np.arange(20000.0)
tr, val = split_train_validation(t, 1000, 50, np.random.default_rng(1))
tr2, val2 = split_train_validation(t, 1000, 50, np.random.default_rng(1))
assert np.array_equal(tr, tr2) and np.array_equal(val, val2)
assert len(val) == 6 * 900 and np.array_equal(val, np.sort(val))  # 6 of 20 blocks, 50 s off each edge
assert np.abs(t[tr][:, None] - t[val][None, :]).min() >= 100
others = ~np.isin(t // 1000, t[val] // 1000) & (t % 1000 >= 50) & (t % 1000 < 950)
assert np.array_equal(np.sort(tr), np.flatnonzero(others)) and not np.array_equal(tr, np.sort(tr))

# more candidates than TRAINING_ROWS: that many, each at most once
drawn = draw_training(np.arange(3 * TRAINING_ROWS), np.random.default_rng(1))
assert len(drawn) == len(np.unique(drawn)) == TRAINING_ROWS

print("ok")
