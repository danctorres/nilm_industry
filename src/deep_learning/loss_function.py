import math
import numpy as np


def poly_4(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        penalty[0, i] = (predicted[0, i] - max_norm_eq[i] / 2) ** 4
    sum_pred = np.full((1, 6), np.sum(predicted, axis=1))
    return (agg - sum_pred) ** 2 + 10 * penalty

def poly_4_d(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        penalty[0, i] = (predicted[0, i] - max_norm_eq[i]) ** 3
    sum_pred = np.full((1, 6), np.sum(predicted, axis=1))
    return -2 * (agg - sum_pred) + 2.5 * penalty


def sum_atan(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        penalty[0, i] = 0.5 * math.atan(100000 * (predicted[0, i] - max_norm_eq[i])) - 0.5 * math.atan(
            100000 * predicted[0, i]) + math.atan(100000)
    sum_arr = np.sum(predicted, axis=1)
    arr = np.full((1, 6), sum_arr)
    return (agg - arr) ** 2 + 10 * penalty

def sum_atan_d(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        penalty[0, i] = 0.5 * math.atan(100000 * (predicted[0, i] - max_norm_eq[i])) - 0.5 * math.atan(
             100000 * predicted[0, i]) + math.atan(100000)
    sum_arr = np.sum(predicted, axis=1)
    arr = np.full((1, 6), sum_arr)
    return -2 * (agg - arr) + 2.5 * penalty


def step(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        if predicted[0, i] > max_norm_eq[i] or predicted[0, i] < max_norm_eq[i]:
            predicted[0, i] = 1.0
        else:
            predicted[0, i] = 0.0
    sum_arr = np.sum(predicted, axis=1)
    arr = np.full((1, 6), sum_arr)
    return (agg - arr) ** 2 + 10 * penalty

def step_d(predicted: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    for i in range(predicted.shape[1]):
        if predicted[0, i] > max_norm_eq[i] or predicted[0, i] < max_norm_eq[i]:
            predicted[0, i] = 1.0
        else:
            predicted[0, i] = 0.0
    sum_arr = np.sum(predicted, axis=1)
    arr = np.full((1, 6), sum_arr)
    return -2 * (agg - arr) + 2.5 * penalty
