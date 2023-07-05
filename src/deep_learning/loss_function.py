import math
import numpy as np
from typing import Optional


def step(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: Optional, min_norm_eq: Optional, n_equipment: int) -> np.ndarray:
    if max_norm_eq is not None and min_norm_eq is not None:
        penalty = np.zeros((1, predicted.shape[1]))
        for i in range(predicted.shape[1]):
            if predicted[0, i] > max_norm_eq[0, i] or predicted[0, i] < min_norm_eq[0, i]:
                penalty[0, i] = predicted[0, i]
        sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
        return (agg - sum_eq) ** 2 + penalty
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return (agg - sum_eq) ** 2

def step_d(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: Optional, min_norm_eq: Optional, n_equipment: int) -> np.ndarray:
    if max_norm_eq is not None and min_norm_eq is not None:
        penalty = np.zeros((1, predicted.shape[1]))
        for i in range(predicted.shape[1]):
            if predicted[0, i] > max_norm_eq[0, i] or predicted[0, i] < min_norm_eq[0, i]:
                penalty[0, i] = 1
        sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
        return -2 * (agg - sum_eq) - penalty
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return -2 * (agg - sum_eq)
