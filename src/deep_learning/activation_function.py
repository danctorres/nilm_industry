import numpy as np

def tanh(x: float) -> float:
    return np.tanh(x)

def tanh_d(x: float) -> float:
    return 1 - np.tanh(x) ** 2

def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))

def sigmoid_d(x: float) -> float:
    return math.exp(-x) / (math.exp(-x) + 1) ** 2

def relu(x: float) -> float:
    if x <= 0:
        return 0
    else:
        return x

def relu_d(x: float) -> float:
    if x <= 0:
        return 0
    else:
        return 1
