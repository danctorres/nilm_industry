import numpy as np

def mse(predicted: np.ndarray, actual: np.ndarray) -> np.ndarray:
    return (predicted - actual) ** 2

def mse_d(predicted: np.ndarray, actual: np.ndarray) -> np.ndarray:
    return 2 * (predicted - actual) / actual.size
