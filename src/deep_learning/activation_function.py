import math
import numpy as np

def tanh(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def tanh_d(x: np.ndarray) -> np.ndarray:
    return 1 - np.tanh(x) ** 2

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + math.exp(-x))

def sigmoid_d(x: np.ndarray) -> np.ndarray:
    return math.exp(-x) / (math.exp(-x) + 1) ** 2

def relu(x: np.ndarray) -> np.ndarray:
    out = x
    for index in range(x.size):
        if x[0, index] <= 0.0:
            out[0, index] = 0.0
    return out

def relu_d(x: np.ndarray) -> np.ndarray:
    out = x
    for index in range(x.size):
        if x[0, index] <= 0.0:
            out[0, index] = 0.0
        else:
            out[0, index] = 1.0
    return out
