#%%
import argparse
import numpy as np
import matplotlib.pyplot as plt

from NN_model import Activation_layer
from NN_model import Connected_layer
from NN_model import NN
from NN_model import activation_function
from NN_model import loss_function
from data_handle import read_csv
from data_handle import save_csv
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


def read_eq_data(number_equipment: int):
    return read_csv.read_csv(f"../../data/processed/HIPE/1_week/equipment_training/eq_training_{number_equipment}.csv")

def read_train_data(number_equipment: int):
    print("--- Reading training data ---")
    sts_train = read_csv.read_csv(f"../../data/processed/HIPE/1_week/state_training/st_training_{number_equipment}.csv")
    agg_train_denorm = read_csv.read_csv(f"../../data/processed/HIPE/1_week/aggregate_training/agg_training_{number_equipment}.csv", 1)
    agg_train = normalize(agg_train_denorm)
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    return resh_agg_train, resh_sts_train, resh_agg_train, agg_train_denorm.min(), agg_train_denorm.max()

def read_validation_data(number_equipment: int):
    print("--- Reading validation data ---")
    sts_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/state_validation/st_validation_{number_equipment}.csv")
    agg_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/aggregate_validation/agg_validation_{number_equipment}.csv", 1)
    timestamp = read_csv.read_csv(f"../../data/processed/HIPE/1_week/aggregate_validation/agg_validation_{number_equipment}.csv", 0)
    eq_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/equipment_validation/eq_validation_{number_equipment}.csv")
    input_val = np.concatenate((sts_val, normalize(agg_val)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return normalize(agg_val), timestamp, eq_val, agg_val.min(), agg_val.max(), agg_val, sts_val


def set_NN(n_equipment: int):
    net = NN.NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer.Connected_layer(1, n_equipment + 1))
    net.set_layer(Activation_layer.Activation_layer(activation_function.relu, activation_function.relu_d))
    net.set_layer(Connected_layer.Connected_layer(n_equipment + 1, n_equipment))
    net.set_layer(Activation_layer.Activation_layer(activation_function.relu, activation_function.relu_d))
    net.set_loss(loss_function.loss_f, loss_function.loss_f_d)
    net.set_epochs(1000)
    return net

def calculate_error(estimations, eq_val, n_equipment) -> List[float]:
    print("--- Calculation MSE ---")
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    return np.round(mse / len(estimations), 4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number_eq", type=int, required=True, help="Number of equipment")
    args = parser.parse_args()

    n_equipment = args.number_eq
    print(f"Number of equipment: {n_equipment}")

    input_train, states_train, agg_train, min_agg, max_agg = read_train_data(n_equipment)

    net = set_NN(n_equipment)

    net.set_max_norm_eq(normalize2(np.max(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))
    net.set_min_norm_eq(normalize2(np.min(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))

    loss_results = net.train(agg_train, states_train, n_equipment, False)

    for key, value in loss_results.items():
        plt.plot(value, label=key)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    plt.show()

    print("")

    agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm, sts_val = read_validation_data(n_equipment)
             
    estimations = denormalize(net.estimate(agg_val_norm, n_equipment), min_agg, max_agg)

    save_csv.save_csv(f"../../results/deep_learning/HIPE/1_week/estimated_active_power_{n_equipment}.csv", agg_val_denorm, estimations, timestamp)
    print(calculate_error(estimations, eq_val, n_equipment))


if __name__ == "__main__":
    main()

# %%
