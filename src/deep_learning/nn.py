"""Fully connected network trained with mini-batch Adam on the sum-constraint loss: the estimates of the machines
that are ON must add up to the aggregate, and a negative estimate of an ON machine is penalised.
    L = (t - sum_j s_j p_j)^2 + sum_j s_j 27 max(-p_j, 0)^3
p: (n, N) estimates, t: (n, 1) aggregate, s: (n, N) 0/1 states.
`stack` trains several networks at once: their weights get a leading run axis, and so does p.
OFF machines are zeroed at estimation time, so they neither count in the sum nor get penalised."""

import copy

import numpy as np

BATCH = 64  # samples per Adam step
BETA1, BETA2 = 0.9, 0.999  # Adam's decay rates of the mean and the mean square of the gradient


def loss(p: np.ndarray, t: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Loss of each sample, shape (n,)."""
    residual = t[:, 0] - np.sum(s * p, axis=-1)
    below = np.maximum(-p, 0.0)
    return residual**2 + np.sum(s * 27.0 * below**3, axis=-1)


def loss_d(p: np.ndarray, t: np.ndarray, s: np.ndarray) -> np.ndarray:
    """dL/dp, shape (n, N). Zero for OFF machines."""
    residual = t - np.sum(s * p, axis=-1, keepdims=True)
    below = np.maximum(-p, 0.0)
    return s * (-2.0 * residual - 81.0 * below**2)


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def relu_d(x: np.ndarray) -> np.ndarray:
    return (x > 0.0).astype(float)


def tanh_d(x: np.ndarray) -> np.ndarray:
    return 1.0 - np.tanh(x) ** 2


class ActivationLayer:
    def __init__(self, f, f_d) -> None:
        self.f, self.f_d = f, f_d

    def forw_prop(self, x: np.ndarray) -> np.ndarray:
        self.input = x
        return self.f(x)

    def back_prop(self, grad: np.ndarray) -> np.ndarray:
        return self.f_d(self.input) * grad


class ConnectedLayer:
    def __init__(self, size_in: int, size_out: int, rng: np.random.Generator) -> None:
        bound = 1 / np.sqrt(size_in)  # wider bounds saturate the tanh of a wide layer from the start
        self.weights = rng.uniform(-bound, bound, (size_in, size_out))
        self.bias = rng.uniform(-bound, bound, (1, size_out))

    def forw_prop(self, x: np.ndarray) -> np.ndarray:
        self.input = x
        return x @ self.weights + self.bias

    def back_prop(self, grad: np.ndarray) -> np.ndarray:
        """Keeps dLoss/dweights and dLoss/dbias summed over the batch, returns dLoss/dinput."""
        self.grads = self.input.swapaxes(-1, -2) @ grad, grad.sum(axis=-2, keepdims=True)
        return grad @ self.weights.swapaxes(-1, -2)


class NN:
    def __init__(self, layers: list, learning_rate: float = 0.01) -> None:
        self.layers = layers
        self.learning_rate = learning_rate

    def estimate(self, x: np.ndarray) -> np.ndarray:
        """Forward pass, (n, inputs) -> (n, machines)."""
        for layer in self.layers:
            x = layer.forw_prop(x)
        return x

    def train(self, x: np.ndarray, t: np.ndarray, s: np.ndarray, epochs: int, rng: np.random.Generator) -> np.ndarray:
        """Adam on the mean loss of each batch, the batches drawn anew every epoch, the learning rate falling linearly
        to 0 (at a constant rate Adam can leave a minimum late). Returns the mean training loss after the last epoch,
        one per run if stacked."""
        dense = [layer for layer in self.layers if isinstance(layer, ConnectedLayer)]
        params = [p for layer in dense for p in (layer.weights, layer.bias)]
        m, v = [np.zeros_like(p) for p in params], [np.zeros_like(p) for p in params]
        step, steps = 0, epochs * -(-len(x) // BATCH)
        for _ in range(epochs):
            order = rng.permutation(len(x))
            for i in range(0, len(x), BATCH):
                rows = order[i : i + BATCH]
                grad = loss_d(self.estimate(x[rows]), t[rows], s[rows]) / len(rows)
                for layer in reversed(self.layers):
                    grad = layer.back_prop(grad)
                rate = self.learning_rate * (1 - step / steps)
                step += 1
                for k, g in enumerate(g for layer in dense for g in layer.grads):
                    m[k] += (1 - BETA1) * (g - m[k])
                    v[k] += (1 - BETA2) * (g**2 - v[k])
                    params[k] -= rate * m[k] / (1 - BETA1**step) / (np.sqrt(v[k] / (1 - BETA2**step)) + 1e-8)
        return np.mean(loss(self.estimate(x), t, s), axis=-1)


def stack(nets: list[NN]) -> NN:
    """The networks as one whose weights have a leading run axis, so each step trains all of them on the same batch.
    Numpy's overhead, not arithmetic, dominates a step on a small batch, so R runs cost little more than one."""
    layers = [copy.copy(layer) for layer in nets[0].layers]
    for i, layer in enumerate(layers):
        if isinstance(layer, ConnectedLayer):
            layer.weights = np.stack([net.layers[i].weights for net in nets])
            layer.bias = np.stack([net.layers[i].bias for net in nets])
    return NN(layers, nets[0].learning_rate)


def pick(net: NN, run: int) -> NN:
    """Run `run` of a stacked network as a network of its own."""
    layers = [copy.copy(layer) for layer in net.layers]
    for layer in layers:
        if isinstance(layer, ConnectedLayer):
            layer.weights, layer.bias = layer.weights[run], layer.bias[run]
    return NN(layers, net.learning_rate)
