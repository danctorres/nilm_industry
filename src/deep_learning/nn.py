# Created by danctorres
"""Fully connected network trained with per-sample SGD on the sum-constraint loss: the estimates of the machines
that are ON must add up to the aggregate, and an ON machine estimated below its lowest training power is penalised.
    L = (t - sum_j s_j p_j)^2 + sum_j s_j 27 max(p_min_j - p_j, 0)^3
p: (n, N) estimates, t: (n, 1) aggregate, s: (n, N) 0/1 states, p_min: (1, N).
OFF machines are zeroed at estimation time, so they neither count in the sum nor get penalised."""

import numpy as np


def loss(p: np.ndarray, t: np.ndarray, s: np.ndarray, p_min: np.ndarray) -> np.ndarray:
    """Loss of each sample, shape (n,)."""
    residual = t[:, 0] - np.sum(s * p, axis=1)
    below = np.maximum(p_min - p, 0.0)
    return residual**2 + np.sum(s * 27.0 * below**3, axis=1)


def loss_d(p: np.ndarray, t: np.ndarray, s: np.ndarray, p_min: np.ndarray) -> np.ndarray:
    """dL/dp, shape (n, N). Zero for OFF machines."""
    residual = t - np.sum(s * p, axis=1, keepdims=True)
    below = np.maximum(p_min - p, 0.0)
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

    def back_prop(self, _learning_rate: float, grad: np.ndarray) -> np.ndarray:
        return self.f_d(self.input) * grad


class ConnectedLayer:
    def __init__(self, size_in: int, size_out: int, rng: np.random.Generator) -> None:
        self.weights = rng.uniform(-1.0, 1.0, (size_in, size_out))
        self.bias = rng.uniform(-1.0, 1.0, (1, size_out))

    def forw_prop(self, x: np.ndarray) -> np.ndarray:
        self.input = x
        return x @ self.weights + self.bias

    def back_prop(self, learning_rate: float, grad: np.ndarray) -> np.ndarray:
        """SGD step for one sample, returns dLoss/dinput computed with the weights before the step."""
        grad_input = grad @ self.weights.T
        self.weights -= learning_rate * self.input.T @ grad
        self.bias -= learning_rate * grad
        return grad_input


class NN:
    def __init__(self, layers: list, learning_rate: float = 0.001) -> None:
        self.layers = layers
        self.learning_rate = learning_rate

    def estimate(self, x: np.ndarray) -> np.ndarray:
        """Forward pass, (n, inputs) -> (n, machines)."""
        for layer in self.layers:
            x = layer.forw_prop(x)
        return x

    def train(self, x: np.ndarray, t: np.ndarray, s: np.ndarray, p_min: np.ndarray, epochs: int) -> float:
        """Per-sample SGD, returns the mean training loss after the last epoch."""
        for _ in range(epochs):
            for i in range(len(x)):
                grad = loss_d(self.estimate(x[i : i + 1]), t[i : i + 1], s[i : i + 1], p_min)
                for layer in reversed(self.layers):
                    grad = layer.back_prop(self.learning_rate, grad)
        return float(np.mean(loss(self.estimate(x), t, s, p_min)))
