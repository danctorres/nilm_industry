# Created by danctorres

#%%
from typing import List
import numpy as np
import matplotlib.pyplot as plt

from NN_model import Activation_layer
from NN_model import Connected_layer_batch
from NN_model import NN_batch
from NN_model import activation_function
from NN_model import loss_function

def calculate_error(estimations, eq_val, n_equipment) -> List[float]:
    mse = np.zeros((1, n_equipment))
    for estimations_array, eq_array in zip(estimations, eq_val.tolist()):
        mse = mse + (estimations_array - eq_array[:n_equipment]) ** 2
    return mse / len(estimations)

def set_NN():
    net = NN_batch.NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer_batch.Connected_layer(3, 5))
    net.set_layer(Activation_layer.Activation_layer(activation_function.relu, activation_function.relu_d))
    net.set_layer(Connected_layer_batch.Connected_layer(5, 2))
    net.set_layer(Activation_layer.Activation_layer(activation_function.relu, activation_function.relu_d))
    net.set_loss(loss_function.loss_f, loss_function.loss_f_d)
    net.set_epochs(10000)
    return net

def main():
    net = set_NN()
    net.set_max_norm_eq(np.array([[0.9, 0.7]]))
    net.set_min_norm_eq(np.array([[0.01, 0.01]]))
    net.set_batch_size(2)

    x_train = np.array([[[0.2]], [[0.5]], [[0.8]], [[1]]])
    states =  np.array([[[1.0, 1.0]], [[1.0, 1.0]], [[1.0, 1.0]], [[1.0, 1.0]]])

    reshaped_x_train = x_train.reshape(-1, x_train.shape[-1])
    batches_x_train =  np.array([reshaped_x_train[i:i + net.batch_size] for i in range(0, len(reshaped_x_train), net.batch_size)])
    reshaped_states = states.reshape(-1, states.shape[-1])
    batches_states =  np.array([reshaped_states[i:i + net.batch_size] for i in range(0, len(reshaped_states), net.batch_size)])

    loss_results = net.train(batches_x_train, batches_states, 1, True)
    # loss_results = net.train(x_train, states, 1, True)

    for key, value in loss_results.items():
        plt.plot(value, label=key)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()

    x_val = np.concatenate((x_train, states), axis = 2)
    estimations = net.estimate(x_val, 1, False)
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
