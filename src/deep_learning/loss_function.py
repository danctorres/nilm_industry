import numpy as np


def step(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, predicted.shape[1]))
    for i in range(predicted.shape[1]):
        # if predicted[0, i] < min_norm_eq[0, i] or predicted[0, i] < max_norm_eq[0, i]:
        if predicted[0, i] < min_norm_eq[0, i]:
            penalty[0, i] = (predicted[0, i]) ** 3
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return (agg - sum_eq) ** 2 + penalty

def step_d(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, predicted.shape[1]))
    for i in range(predicted.shape[1]):
        # if predicted[0, i] < min_norm_eq[0, i] or predicted[0, i] < max_norm_eq[0, i]:
        if predicted[0, i] < min_norm_eq[0, i]:
            penalty[0, i] = 3 * predicted[0, i] ** 2
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return -2 * (agg - sum_eq) - penalty
