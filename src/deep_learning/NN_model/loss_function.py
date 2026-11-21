# Created by danctorres
#
# Sum-constraint loss: the estimates of the machines that are ON must add up to the aggregate,
# and an ON machine estimated below its lowest training power is penalised.
#   L = (t - sum_j s_j p_j)^2 + sum_j s_j 27 max(p_min_j - p_j, 0)^3
# p: (n, N) estimates, t: (n, 1) aggregate, s: (n, N) 0/1 states, p_min: (1, N).
# OFF machines are zeroed at estimation time, so they neither count in the sum nor get penalised.

import numpy as np


def loss(p: np.ndarray, t: np.ndarray, s: np.ndarray, p_min: np.ndarray) -> np.ndarray:
    """Loss of each sample, shape (n,)."""
    residual = t[:, 0] - np.sum(s * p, axis=1)
    below = np.maximum(p_min - p, 0.0)
    return residual ** 2 + np.sum(s * 27.0 * below ** 3, axis=1)


def loss_d(p: np.ndarray, t: np.ndarray, s: np.ndarray, p_min: np.ndarray) -> np.ndarray:
    """dL/dp, shape (n, N). Zero for OFF machines."""
    residual = t - np.sum(s * p, axis=1, keepdims=True)
    below = np.maximum(p_min - p, 0.0)
    return s * (-2.0 * residual - 81.0 * below ** 2)
