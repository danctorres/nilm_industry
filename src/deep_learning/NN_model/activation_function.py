# Created by danctorres

import math
import numpy as np


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0)

def relu_d(x: np.ndarray) -> np.ndarray:
    out = x
    for index in range(x.size):
        if x[0, index] <= 0.0:
            out[0, index] = 0.0
        else:
            out[0, index] = 1.0
    return out

def tanh(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def tanh_d(x: np.ndarray) -> np.ndarray:
    return 1 - np.tanh(x) ** 2

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + math.exp(-x))

def sigmoid_d(x: np.ndarray) -> np.ndarray:
    return sigmoid(x) * (1 - sigmoid(x))
