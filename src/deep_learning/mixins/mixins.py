# Created by danctorres

import numpy as np
import math
from typing import List


def normalize(data: np.ndarray) -> np.ndarray:
    min_val = data.min()
    max_val = data.max()
    data_norm = np.empty(data.shape)
    for i, value in enumerate(data):
        data_norm[i] = (value - min_val) / (max_val - min_val)
    return data_norm

def normalize2(data: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    data_norm = np.empty(data.shape)
    for i, value in enumerate(data):
        data_norm[i] = (value - min_val) / (max_val - min_val)
    return data_norm

def normalize_pi(data: np.ndarray) -> np.ndarray:
    min_val = -math.pi
    max_val = math.pi
    data_norm = np.empty(data.shape)
    for i, value in enumerate(data):
        data_norm[i] = (value - min_val) / (max_val - min_val)
    return data_norm

def denormalize(data_norm: List[np.ndarray], min_val: float, max_val: float) -> np.ndarray:
    for i, value in enumerate(data_norm):
        data_norm[i] = np.round(value * (max_val - min_val) + min_val, 4)
    return data_norm

def calculate_error(estimations: List, eq_val: np.ndarray, n_equipment: int) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    error = np.round(mse / len(estimations), 4)
    print(f" MSE {error}")
    return error

def calculate_error_different_zero(estimations: List, eq_val: np.ndarray, sts_val: np.ndarray, n_equipment: int) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array, sts_array in zip(estimations, eq_val.tolist(), sts_val):
        for idx in range(len(sts_array)):
            if (sts_array[idx] == 1 and estimations_array[0, idx] == 0):
                mse[0, idx] += 1
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    one_num = []
    for i in range(n_equipment):
        one_num.append(np.sum(sts_val[:, i] == 1))
    error = np.round([x / y for x, y in zip(mse, one_num)], 4) # change this, divide by the number of state == 1
    print(f" MSE {error}")
    return error

def post_estimation_zeros(estimations: List, states: np.ndarray, n_equipment: int) -> List:
    new_estimation = []
    for est, st in zip(estimations, states):
        new_estimation.append(est * st.reshape(n_equipment))
    return new_estimation
