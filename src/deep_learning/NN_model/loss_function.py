# Created by danctorres

import numpy as np


def loss_f(predicted: np.ndarray, agg: np.ndarray, state: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, predicted.shape[1]))
    for i in range(predicted.shape[1]):
        # if predicted[0, i] < min_norm_eq[0, i] or predicted[0, i] < max_norm_eq[0, i]:
        if predicted[0, i] < min_norm_eq[0, i]:
            penalty[0, i] = abs(3 * predicted[0, i]) ** 3
    sum_eq = np.full((1, n_equipment), np.sum(predicted * state, axis=1))
    loss = (agg - sum_eq) ** 2 + penalty
    return loss

def loss_f_d(predicted: np.ndarray, agg: np.ndarray, state: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, predicted.shape[1]))
    for i in range(predicted.shape[1]):
        # if predicted[0, i] < min_norm_eq[0, i] or predicted[0, i] < max_norm_eq[0, i]:
        if (predicted[0, i] < min_norm_eq[0, i]):
            penalty[0, i] = 81 * (predicted[0, i] - min_norm_eq[0, i])** 2
    sum_eq = np.full((1, n_equipment), np.sum(predicted * state, axis=1))
    loss_d = -2 * (agg - sum_eq) - penalty
    return loss_d
