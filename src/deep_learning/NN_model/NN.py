# Created by danctorres

import numpy as np
from NN_model.loss_function import loss, loss_d


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
