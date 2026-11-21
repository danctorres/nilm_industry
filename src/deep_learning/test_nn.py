"""Self-check of the network and its loss: python3 src/deep_learning/test_nn.py"""

import numpy as np
from main import build, inputs
from nn import loss, loss_d

rng = np.random.default_rng(0)

# The gradient is the exact derivative of the loss (penalty active too) and zero for OFF machines.
p = rng.uniform(-0.5, 0.5, (4, 3))
t = rng.uniform(0.0, 1.0, (4, 1))
s = np.array([[1, 0, 1], [0, 0, 1], [1, 1, 1], [0, 1, 0]], dtype=float)
p_min = np.full((1, 3), 0.1)
g = loss_d(p, t, s, p_min)
assert np.all(g[s == 0] == 0.0), g
h = 1e-6
for i, j in np.ndindex(p.shape):
    step = np.zeros_like(p)
    step[i, j] = h
    numeric = (loss(p + step, t, s, p_min)[i] - loss(p - step, t, s, p_min)[i]) / (2 * h)
    assert abs(numeric - g[i, j]) < 1e-5, (i, j, numeric, g[i, j])

# Three machines drawing 0.2, 0.3 and 0.4 when ON: after training, the ON estimates sum to the aggregate.
s = rng.integers(0, 2, (40, 3)).astype(float)
t = s @ np.array([[0.2], [0.3], [0.4]])
x = inputs("state", t / t.max(), s)
net = build("state", 3, rng)
net.learning_rate = 0.01
print(f"loss {net.train(x, t, s, np.zeros((1, 3)), 500):.2e}")
gap = np.abs(np.sum(net.estimate(x) * s, axis=1, keepdims=True) - t).max()
assert gap < 0.02, gap
print(f"ok, largest |sum of estimates - aggregate| = {gap:.4f}")
