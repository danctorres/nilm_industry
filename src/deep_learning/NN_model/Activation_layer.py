# Created by danctorres

import numpy as np


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
