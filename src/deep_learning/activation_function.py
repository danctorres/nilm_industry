import numpy as np

def activation(input: float) -> float:
    return np.tanh(input)

def activation_d(input: float) -> float:
    return 1 - np.tanh(input) ** 2
