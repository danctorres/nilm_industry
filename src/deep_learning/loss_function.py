import numpy as np

def loss(predicted: np.ndarray, actual: np.ndarray) -> np.ndarray:
    return (actual - predicted) ** 2

def loss_d(predicted: np.ndarray, actual: np.ndarray) -> np.ndarray:
    return -2 * (actual - predicted)
