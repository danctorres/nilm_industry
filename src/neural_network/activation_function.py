import numpy as np

def tanh(input: float) -> float:
    return np.tanh(input)

def tanh_d(input: float) -> float:
    return 1 - np.tanh(input) ** 2
