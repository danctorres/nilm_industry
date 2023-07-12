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

def denormalize(data: List[np.ndarray], min_val: float, max_val: float) -> np.ndarray:
    for i, value in enumerate(data):
        data[i] = value * (max_val - min_val) + min_val
    return data

def read_eq_data():
    return read_csv("../../data/processed/IMDELD/data_6_equipment/equipment_training.csv")

def read_train_data():
    print("--- Reading training data ---")
    sts_train = read_csv("../../data/processed/IMDELD/data_6_equipment/on_off_training.csv")
    agg_train_denorm = read_csv("../../data/processed/IMDELD/data_6_equipment/aggregate_training.csv", 1)
    agg_train = normalize(agg_train_denorm)
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    return resh_input_train, resh_sts_train, resh_agg_train, agg_train_denorm.min(), agg_train_denorm.max()

def read_validation_data():
    print("--- Reading validation data ---")
    sts_val = read_csv("../../data/processed/IMDELD/data_6_equipment/on_off_validation.csv")
    agg_val_denorm = read_csv("../../data/processed/IMDELD/data_6_equipment/aggregate_validation.csv", 1)
    timestamp = read_csv("../../data/processed/IMDELD/data_6_equipment/aggregate_validation.csv", 0)
    eq_val = read_csv("../../data/processed/IMDELD/data_6_equipment/equipment_validation.csv")
    # resh_sts_val = np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))
    # resh_agg_val = np.reshape(agg_val, (agg_val.shape[0], 1, agg_val.shape[1]))
    input_val = np.concatenate((sts_val, normalize(agg_val_denorm)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return resh_input_val, timestamp, eq_val, agg_val_denorm.min(), agg_val_denorm.max(), agg_val_denorm

def set_NN():
    net = NN()
    net.set_learning_rate(0.1)    # bigger value for the learning rate causes overshoot
    net.set_layer(Connected_layer(1, 7))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(7, 6))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(step, step_d)
    net.set_epochs(100)
    return net

def calculate_error(estimations, eq_val, n_equipment) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    return mse / len(estimations)


def main():
    input_train, states_train, agg_train, min_agg, max_agg = read_train_data()
    n_equipment = 6
    net = set_NN(n_equipment)

    net.set_max_norm_eq(normalize2(np.array([[2000.0, 1500.0, 6000.0, 6000.0, 100000.0, 100000.0]]), min_agg, max_agg))
    net.set_min_norm_eq(normalize2(np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]), min_agg, max_agg))

    # net.set_max_norm_eq(normalize2(np.max(read_eq_data(), axis=0), min_agg, max_agg))
    # net.set_min_norm_eq(normalize2(np.min(read_eq_data(), axis=0), min_agg, max_agg))

    loss_results = net.train(agg_train, n_equipment)

    for key, value in loss_results.items():
        plt.plot(value, label=key)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()

    print("")
    agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm = read_validation_data()

    estimations = denormalize(net.estimate(normalize(agg_val_denorm)), min_agg, max_agg)

    save_csv("../../results/deep_learning/IMDELD/estimated_active_power.csv", agg_val_denorm, estimations, timestamp)
    print(calculate_error(estimations, eq_val, n_equipment))


if __name__ == "__main__":
    main()
