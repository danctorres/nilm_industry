import numpy as np
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

def denormalize(data_norm: List[np.ndarray], min_val: float, max_val: float) -> np.ndarray:
    for i, value in enumerate(data_norm):
        data_norm[i] = np.round(value * (max_val - min_val) + min_val, 4)
    return data_norm

def calculate_error(estimations, eq_val, n_equipment) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    error = np.round(mse / len(estimations), 4)
    print(f" MSE {error}")
    return error

def calculate_error_different_zero(estimations, eq_val, sts_val, n_equipment) -> List[float]:
    # only calculate error for values different than state 0
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array, sts_array in zip(estimations, eq_val.tolist(), sts_val):
        for idx in range(len(sts_array)):
            if (sts_array[idx] == 1 and estimations_array[0, idx] == 0):
                mse[0, idx] += 1
                # change this
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    error = np.round(mse / len(estimations), 4)
    print(f" MSE {error}")
    return error

def post_estimation_zeros(estimations: List, states: np.ndarray, n_equipment: int) -> List:
    new_estimation = []
    for est, st in zip(estimations, states):
        new_estimation.append(est * st.reshape(n_equipment))
    return new_estimation
