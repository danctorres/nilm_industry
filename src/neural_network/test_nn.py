"""Self-check of the network and its loss: python3 src/neural_network/test_nn.py"""

import tempfile
from pathlib import Path

import nn
import numpy as np
import pandas as pd
from main import build, inputs, main
from nn import ConnectedLayer, loss, loss_d, pick, stack

rng = np.random.default_rng(0)

# loss_d matches the loss's numeric derivative (penalty active too) and is zero for OFF machines.
p = rng.uniform(-0.5, 0.5, (4, 3))
t = rng.uniform(0.0, 1.0, (4, 1))
s = np.array([[1, 0, 1], [0, 0, 1], [1, 1, 1], [0, 1, 0]], dtype=float)
g = loss_d(p, t, s)
assert np.all(g[s == 0] == 0.0), g
h = 1e-6
for i, j in np.ndindex(p.shape):
    step = np.zeros_like(p)
    step[i, j] = h
    numeric = (loss(p + step, t, s)[i] - loss(p - step, t, s)[i]) / (2 * h)
    assert abs(numeric - g[i, j]) < 1e-5, (i, j, numeric, g[i, j])

# Three machines drawing 0.2, 0.3 and 0.4 when ON: after training, the ON estimates sum to the total.
s = rng.integers(0, 2, (40, 3)).astype(float)
t = s @ np.array([[0.2], [0.3], [0.4]])
x = inputs("state", t / t.max(), s)
net = build("state", 3, rng)
print(f"loss {net.train(x, t, s, 500, rng):.2e}")
gap = np.abs(np.sum(net.estimate(x) * s, axis=1, keepdims=True) - t).max()
assert gap < 0.02, gap
print(f"largest |sum of estimates - aggregate| = {gap:.4f}")

# Trained stacked or one by one, on the same batches, the networks end with the same weights and losses.
nn.BATCH = 16  # so each epoch has several batches
alone = [build("state", 3, np.random.default_rng(r)) for r in (1, 2)]
alone_losses = [n.train(x, t, s, 2, np.random.default_rng(0)) for n in alone]
stacked = stack([build("state", 3, np.random.default_rng(r)) for r in (1, 2)])
assert np.allclose(stacked.train(x, t, s, 2, np.random.default_rng(0)), alone_losses, rtol=1e-12, atol=0)
for run, n in enumerate(alone):
    for a, b in zip(pick(stacked, run).layers, n.layers, strict=True):
        if isinstance(a, ConnectedLayer):
            assert np.array_equal(a.weights, b.weights) and np.array_equal(a.bias, b.bias), run

# Weight decay pulls the weights toward 0: the same network trained with more of it ends with smaller weights.
nets = [build("state", 3, np.random.default_rng(3)) for _ in range(2)]
nets[1].weight_decay = 1.0
for n in nets:
    n.train(x, t, s, 20, np.random.default_rng(0))
size = [sum(np.sum(layer.weights**2) for layer in n.layers if isinstance(layer, ConnectedLayer)) for n in nets]
assert size[1] < size[0], size

# end to end, averaging two runs: reads the split files and writes one estimate per machine per validation row,
# with OFF machines at 0 and the ON ones adding up to the total (barely trained, the network alone doesn't)
with tempfile.TemporaryDirectory() as name:
    d = Path(name) / "HIPE" / "3"
    d.mkdir(parents=True)
    ts = pd.date_range("2017-10-23", periods=40, freq="s").strftime("%d-%b-%Y %H:%M:%S")
    for split, rows in (("training", slice(10, None)), ("validation", slice(10))):
        pd.DataFrame({"timestamp": ts, "active_power": t[:, 0]})[rows].to_csv(d / f"aggregate_{split}.csv", index=False)
        pd.DataFrame({"timestamp": ts, **dict(enumerate(s.T))})[rows].to_csv(d / f"states_{split}.csv", index=False)
        pd.DataFrame({"timestamp": ts, **dict(enumerate((s * [0.2, 0.3, 0.4]).T))})[rows].to_csv(
            d / f"equipment_{split}.csv", index=False
        )
    argv = ["--dataset", "hipe", "--mode", "plain", "--machines", "3", "--runs", "2", "--epochs", "2"]
    main([*argv, "--data-root", name, "--results-root", name])
    out = pd.read_csv(Path(name) / "plain" / "HIPE" / "3.csv")
    assert list(out.columns) == ["Timestamp", "Aggregate_Active_Power", "Estimate_0", "Estimate_1", "Estimate_2"]
    assert list(out.Timestamp) == list(ts[:10]) and (out.iloc[:, 2:].to_numpy()[s[:10] == 0] == 0).all()
    assert np.allclose(out.iloc[:, 2:].sum(axis=1), out.Aggregate_Active_Power) and (out.iloc[:, 2:] >= 0).all().all()
    pd.read_csv(d / "states_validation.csv")[::-1].to_csv(d / "states_validation.csv", index=False)
    try:
        main([*argv, "--data-root", name, "--results-root", name])
        raise AssertionError("timestamps that differ must be rejected")
    except SystemExit:
        pass
print("ok")
