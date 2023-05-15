import numpy as np
import math

def loss(predicted: np.ndarray, state: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    return (agg - predicted * state) ** 2

def loss_d(predicted: np.ndarray, state: np.ndarray, agg: np.ndarray, max_norm_eq: np.ndarray) -> np.ndarray:
    penalty = np.array([[0, 0, 0, 0, 0, 0]])
    # arctan(-x) + arctan(x - 0.5) - (arctan(-1 / 4) + arctan(1 / 4 - 0.5))

    for i in range(predicted.shape[1]):
        penalty[0, i] = 1 / ((predicted[0, i] - max_norm_eq[i]) ** 2 + 1) - 1 / (predicted[0, i] ** 2 + 1)

    # if predicted[0, i] < 0 or predicted[0, i] > max_norm_eq[i]:
    #     # Two sigmoid functions
    #     # f(x) = (1 / (1 + e^(x + 100))) +  (1 / (1 + e^(-x + 100)))
    #     penalty[0, i] = 10

    sum_arr = np.sum(predicted, axis=1)
    arr = np.full((1, 6), sum_arr)

    # print(-2 * (agg - arr) + penalty)

    return -2 * (agg - arr) + penalty
