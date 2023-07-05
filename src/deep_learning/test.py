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


def set_NN():
    net = NN()
    net.set_learning_rate(0.1)
    net.set_layer(Connected_layer(1, 3))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(3, 2))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(step, step_d)
    net.set_epochs(10000)
    return net

def main():
    net = set_NN()
    net.set_max_norm_eq(np.array([[1.0, 1.0]]))
    net.set_min_norm_eq(np.array([[0.0, 0.0]]))

    x_train = np.array([[[0.2]], [[0.5]], [[0.8]], [[1]]])
    loss_results = net.train(x_train, 1)

    fig, axs = plt.subplots(len(loss_results), 1, figsize=(8, 6))
    for i, (key, value) in enumerate(loss_results.items()):
        axs[i].plot(value)
        axs[i].set_xlabel('X-axis')
        axs[i].set_ylabel('Y-axis')
        axs[i].set_title(key)
    plt.tight_layout()
    plt.show()

    estimations = net.estimate(x_train)

    sums = []
    for inner_array in estimations:
        sum_inner_array = np.sum(inner_array)
        sums.append(sum_inner_array)

    print(f"Estimations {estimations}")
    print(f"Expected {x_train.flatten()}")
    print(f"Sums {sums}")
    print(f"Error {sums - x_train.flatten()}")
    # assert np.all((estimations - y_train) < 0.1)

if __name__ == "__main__":
    main()
