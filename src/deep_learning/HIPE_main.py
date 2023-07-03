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


def read_eq_data():
    return read_csv('../../data/processed/HIPE/1_week/equipment_training.csv')

def read_train_data():
    print('Reading training data')
    sts_train = read_csv('../../data/processed/HIPE/1_week/on_off_training.csv')
    agg_train = read_csv('../../data/processed/HIPE/1_week/aggregate_training.csv', 1)
    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    return resh_input_train, resh_sts_train, resh_agg_train

def read_validation_data():
    print('Reading validation data')
    sts_val = read_csv('../../data/processed/HIPE/1_week/on_off_validation.csv')
    agg_val = read_csv('../../data/processed/HIPE/1_week/aggregate_validation.csv', 1)
    timestamp = read_csv('../../data/processed/HIPE/1_week/aggregate_validation.csv', 0)
    eq_val = read_csv('../../data/processed/HIPE/1_week/equipment_validation.csv')
    input_val = np.concatenate((sts_val, agg_val), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return resh_input_val, timestamp, eq_val

def set_NN():
    net = NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer(11, 13))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(13, 10))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(poly_4, poly_4_d)
    net.set_epochs(100)
    return net

def calculate_error(estimations, eq_val) -> List[float]:
    mse = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array) ** 2
    return mse / len(estimations)


def main():
    # Read data for training
    input_train, states_train, agg_train = read_train_data()

    # Set NN
    net = set_NN()

    net.set_max_norm_eq(np.max(read_eq_data(), axis=0))
    net.set_min_norm_eq(np.min(read_eq_data(), axis=0))

    loss_results = net.train(input_train, agg_train, states_train, 10)

    fig, axs = plt.subplots(5, 2)
    x = range(1, len(loss_results[0]) + 1)
    axs[0, 0].plot(x, loss_results[0])
    axs[0, 1].plot(x, loss_results[1])
    axs[1, 0].plot(x, loss_results[2])
    axs[1, 1].plot(x, loss_results[3])
    axs[2, 0].plot(x, loss_results[4])
    axs[2, 1].plot(x, loss_results[5])
    axs[3, 0].plot(x, loss_results[6])
    axs[3, 1].plot(x, loss_results[7])
    axs[4, 0].plot(x, loss_results[8])
    axs[4, 1].plot(x, loss_results[9])
    axs[0, 0].set_title('Equipment 0')
    axs[0, 1].set_title('Equipment 1')
    axs[1, 0].set_title('Equipment 2')
    axs[1, 1].set_title('Equipment 3')
    axs[2, 0].set_title('Equipment 4')
    axs[2, 1].set_title('Equipment 5')
    axs[3, 0].set_title('Equipment 6')
    axs[3, 1].set_title('Equipment 7')
    axs[4, 0].set_title('Equipment 8')
    axs[4, 1].set_title('Equipment 9')
    fig.suptitle('Loss per equipment')
    fig.tight_layout()
    plt.show()

    # Read data for validation
    agg_val, timestamp, eq_val = read_validation_data()
    estimations = net.estimate(agg_val)

    save_csv('../../results/deep_learning/HIPE/1_week/estimated_active_power.csv', agg_val, estimations, timestamp)
    print(calculate_error(estimations, eq_val))


if __name__ == '__main__':
    main()
