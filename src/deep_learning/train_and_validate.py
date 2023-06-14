import numpy as np
import matplotlib.pyplot as plt

from Activation_layer import Activation_layer
from Connected_layer import Connected_layer
from NN import NN
from activation_function import tanh, tanh_d
from loss_function import poly_4, poly_4_d
from read_csv import read_csv
from save_csv import save_csv
from typing import List


def read_train_data():
    sts_train = read_csv('../../data/processed/data_6_equipment/on_off_training.csv')
    agg_train_denorm = read_csv('../../data/processed/data_6_equipment/aggregate_training.csv', 1)

    # Format data
    agg_train = normalize(agg_train_denorm)

    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))

    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))

    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))

    return resh_input_train, resh_sts_train, resh_agg_train, agg_train_denorm.min(), agg_train_denorm.max()

def read_validation_data():
    sts_val = read_csv('../../data/processed/data_6_equipment/on_off_validation.csv')
    agg_val_denorm = read_csv('../../data/processed/data_6_equipment/aggregate_validation.csv', 1)
    timestamp = read_csv('../../data/processed/data_6_equipment/aggregate_validation.csv', 0)
    eq_val = read_csv('../../data/processed/data_6_equipment/equipment_validation.csv')

    # resh_sts_val = np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))
    # resh_agg_val = np.reshape(agg_val, (agg_val.shape[0], 1, agg_val.shape[1]))

    input_val = np.concatenate((sts_val, normalize(agg_val_denorm)), axis = 1)

    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return resh_input_val, timestamp, eq_val

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
        data[i] = np.round(value * (max_val - min_val) + min_val, 2)
    return data

def set_NN():
    net = NN()
    net.set_learning_rate(0.001)    # big value for the learning rate causes overshoot
    net.set_layer(Connected_layer(7, 14))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(7, 6))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(poly_4, poly_4_d)
    net.set_epochs(100)
    return net

def calculate_error(estimations, eq_val) -> List[float]:
    mse = [0, 0, 0, 0, 0, 0]
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array) ** 2
    return mse / len(estimations)


def main():
    # Read data for training
    input_train, states_train, agg_train, min_agg, max_agg = read_train_data()

    # Set NN
    net = set_NN()
    net.set_max_norm_eq(normalize2(np.array([2000, 1500, 6000, 6000, 100000, 100000]), min_agg, max_agg))

    loss_results = net.train(input_train, states_train, agg_train)

    # Plot loss
    # print(loss_results)
    plt.plot(range(1, len(loss_results[3]) + 1), loss_results[3], '.')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Scatter Plot')
    plt.show()

    # Read data for validation
    agg_val, timestamp, eq_val = read_validation_data()
    out = net.estimate(agg_val)

    estimations = denormalize(out, min_agg, max_agg)

    # print(estimations)

    save_csv('../../results/deep_learning/estimated_active_power.csv', estimations, timestamp)
    print(calculate_error(estimations, eq_val))


if __name__ == '__main__':
    main()
