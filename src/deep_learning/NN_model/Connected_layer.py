# Created by danctorres

import numpy as np


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
