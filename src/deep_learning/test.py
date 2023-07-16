#%%
import numpy as np
import matplotlib.pyplot as plt

from Activation_layer import Activation_layer
from Connected_layer import Connected_layer
from NN import NN
from activation_function import tanh, tanh_d
from loss_function import loss_f, loss_f_d
from typing import List

def calculate_error(estimations, eq_val, n_equipment) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    return mse / len(estimations)

def set_NN():
    net = NN()
    net.set_learning_rate(0.1)
    net.set_layer(Connected_layer(3, 5))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_layer(Connected_layer(5, 2))
    net.set_layer(Activation_layer(tanh, tanh_d))
    net.set_loss(loss_f, loss_f_d)
    net.set_epochs(10000)
    return net

def main():
    net = set_NN()
    net.set_max_norm_eq(np.array([[0.9, 0.7]]))
    net.set_min_norm_eq(np.array([[0.0, 0.0]]))

    x_train = np.array([[[0.2]], [[0.5]], [[0.8]], [[1]]])
    states =  np.array([[[1.0, 1.0]], [[1.0, 1.0]], [[1.0, 1.0]], [[1.0, 1.0]]])
    loss_results = net.train(x_train, states, 1, True)

    for key, value in loss_results.items():
        plt.plot(value, label=key)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()

    x_val = np.concatenate((x_train, states), axis = 2)
    estimations = net.estimate(x_val, 1)
    print(estimations)
    sums = []
    for inner_array in estimations:
        sum_inner_array = np.sum(inner_array)
        sums.append(sum_inner_array)

    print(f"Estimations {estimations}")
    print(f"Expected {x_train.flatten()}")
    print(f"Sums {sums}")
    print(f"Error {sums - x_train.flatten()}")
    # assert np.all((estimations - y_train) < 0.1)

    print(calculate_error(estimations, x_train, 1))


if __name__ == "__main__":
    main()

# %%
