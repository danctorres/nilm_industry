import math
import numpy as np


def poly_4(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        penalty[0, i] = abs(predicted[0, i] - max_norm_eq[i] / 2) ** 4
    sum_pred = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return (agg - sum_pred) ** 2 + 10 * penalty

def poly_4_d(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        penalty[0, i] = abs(predicted[0, i] - max_norm_eq[i]) ** 3
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    # print(np.sum(np.multiply(states, predicted), axis=1))
    return -2 * (agg - sum_eq) + 2.5 * penalty

def sum_atan(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        penalty[0, i] = 0.5 * math.atan(100000 * (predicted[0, i] - max_norm_eq[i])) - 0.5 * math.atan(
            100000 * predicted[0, i]) + math.atan(100000)
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return (agg - sum_eq) ** 2 + 10 * penalty

def sum_atan_d(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        penalty[0, i] = 0.5 * math.atan(100000 * (predicted[0, i] - max_norm_eq[i])) - 0.5 * math.atan(
             100000 * predicted[0, i]) + math.atan(100000)
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    return -2 * (agg - sum_eq) + 2.5 * penalty


def step(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        if predicted[0, i] > max_norm_eq[i] or predicted[0, i] < min_norm_eq[i]:
            penalty[0, i] = (5 * predicted[0, i]) ** 2
        else:
            if (states[0, i] == 0 and predicted[0, i] != 0.0) or (states[0, i] != 0 and predicted[0, i] == 0.0):
                penalty[0, i] = (8 * predicted[0, i]) ** 2
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    # loss_function = (agg - sum_eq) ** 2 + penalty
    # for i in range(predicted.shape[1]):
    #     if states[0, i] == 0:
    #         loss_function[0, i] = (0 - predicted[0, i]) ** 2
    return (agg - sum_eq) ** 2 + penalty

def step_d(predicted: np.ndarray, agg: np.ndarray, states: np.ndarray, max_norm_eq: np.ndarray, min_norm_eq: np.ndarray, n_equipment: int) -> np.ndarray:
    penalty = np.zeros((1, n_equipment))
    for i in range(predicted.shape[1]):
        if predicted[0, i] > max_norm_eq[i] or predicted[0, i] < min_norm_eq[i]:
            penalty[0, i] = 50 * predicted[0, i]
        else:
            if (states[0, i] == 0 and predicted[0, i] != 0.0) or (states[0, i] != 0 and predicted[0, i] == 0.0):
                penalty[0, i] = 98 * predicted[0, i]
    sum_eq = np.full((1, n_equipment), np.sum(predicted, axis=1))
    # loss_function = -2 * (agg - sum_eq) + penalty
    # for i in range(predicted.shape[1]):
    #     if states[0, i] == 0:
    #         loss_function[0, i] = 2 * (0 - predicted[0, i])
    return -2 * (agg - sum_eq) + penalty
