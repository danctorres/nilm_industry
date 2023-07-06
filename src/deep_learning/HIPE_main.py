import numpy as np
import matplotlib.pyplot as plt

from Activation_layer import Activation_layer
from Connected_layer import Connected_layer
from NN import NN
from activation_function import tanh, tanh_d
from loss_function import step, step_d
from read_csv import read_csv
from save_csv import save_csv
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
        data_norm[i] = value * (max_val - min_val) + min_val
    return data_norm

def read_eq_data():
    return read_csv("../../data/processed/HIPE/1_week/equipment_training.csv")

def read_train_data():
    print("--- Reading training data ---")
    sts_train = read_csv("../../data/processed/HIPE/1_week/on_off_training.csv")
    agg_train_denorm = read_csv("../../data/processed/HIPE/1_week/aggregate_training/agg_training_2.csv", 1)
    agg_train = normalize(agg_train_denorm)
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    return resh_agg_train, resh_sts_train, resh_agg_train, agg_train_denorm.min(), agg_train_denorm.max()

def read_validation_data():
    print("--- Reading validation data ---")
    sts_val = read_csv("../../data/processed/HIPE/1_week/on_off_validation.csv")
    agg_val = read_csv("../../data/processed/HIPE/1_week/aggregate_validation/agg_validation_2.csv", 1)
    timestamp = read_csv("../../data/processed/HIPE/1_week/aggregate_validation/agg_validation_2.csv", 0)
    eq_val = read_csv("../../data/processed/HIPE/1_week/equipment_validation.csv")
    input_val = np.concatenate((sts_val, normalize(agg_val)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return normalize(agg_val), timestamp, eq_val, agg_val.min(), agg_val.max(), agg_val


def set_NN(n_equipment: int):
    net = NN()
    net.set_learning_rate(0.1)
    net.set_layer(Connected_layer(1, 5))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(5, n_equipment))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(step, step_d)
    net.set_epochs(100)
    return net

def calculate_error(estimations, eq_val) -> List[float]:
    mse = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array) ** 2
    return mse / len(estimations)


def main():
    input_train, states_train, agg_train, min_agg, max_agg = read_train_data()
    n_equipment = 2

    net = set_NN(n_equipment)

    net.set_max_norm_eq(normalize2(np.array([[0.9, 9.0, 0.5, 0.5, 8.2, 0.1, 1.1, 0.9, 0.1]]), min_agg, max_agg))
    net.set_min_norm_eq(normalize2(np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]), min_agg, max_agg))


    loss_results = net.train(agg_train, n_equipment)

    for key, value in loss_results.items():
        plt.plot(value, label=key)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()

    print("")

    # Validation
    agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm = read_validation_data()
    estimations = denormalize(net.estimate(agg_val_norm), min_agg, max_agg)

    save_csv("../../results/deep_learning/HIPE/1_week/estimated_active_power.csv", agg_val_denorm, estimations, timestamp)


if __name__ == "__main__":
    main()
