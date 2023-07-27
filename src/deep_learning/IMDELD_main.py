#%%
import os
import numpy as np
# import matplotlib.pyplot as plt

from NN_model import Activation_layer
from NN_model import Connected_layer
from NN_model import NN
from NN_model import activation_function
from NN_model import loss_function
from data_handle import read_csv
from data_handle import save_csv
from data_handle import read_estimations_csv
from mixins import mixins
from typing import List


def read_eq_data():
    return read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/equipment_training.csv")

def read_train_data():
    print("--- Reading training data ---")
    sts_train = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/on_off_training.csv")
    agg_train_denorm = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/aggregate_training.csv", 1)
    agg_train = mixins.normalize(agg_train_denorm)
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    input_train = np.concatenate((sts_train, agg_train), axis=1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    return resh_agg_train, resh_sts_train, resh_agg_train, agg_train_denorm.min(), agg_train_denorm.max()

def read_validation_data():
    print("--- Reading validation data ---")
    sts_val = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/on_off_validation.csv")
    agg_val = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/aggregate_validation.csv", 1)
    timestamp = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/aggregate_validation.csv", 0)
    eq_val = read_csv.read_csv(f"../../data/processed/IMDELD/data_6_equipment/equipment_validation.csv")
    input_val = np.concatenate((sts_val, mixins.normalize(agg_val)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return mixins.normalize(agg_val), timestamp, eq_val, agg_val.min(), agg_val.max(), agg_val, sts_val


def set_NN():
    net = NN.NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer.Connected_layer(1 + 6, 7 + 1))
    net.set_layer(Activation_layer.Activation_layer(activation_function.tanh, activation_function.tanh_d))
    net.set_layer(Connected_layer.Connected_layer(7 + 1, 6))
    net.set_layer(Activation_layer.Activation_layer(activation_function.tanh, activation_function.tanh_d))
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
    n_equipment = 6

    input_train, states_train, agg_train, min_agg, max_agg = read_train_data()
    agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm, sts_val = read_validation_data()
    data_val = np.concatenate ( (np.reshape(agg_val_norm, (agg_val_norm.shape[0], 1, 1)) , np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))), axis = 2)

    for idx in range(20):
        net = set_NN()

        net.set_max_norm_eq(mixins.normalize2(np.max(read_eq_data(), axis=0).reshape(1, n_equipment), min_agg, max_agg))
        net.set_min_norm_eq(mixins.normalize2(np.min(read_eq_data(), axis=0).reshape(1, n_equipment), min_agg, max_agg))

        loss_results = net.train(agg_train, states_train, n_equipment, True)

        # for key, value in loss_results.items():
        #     plt.plot(value, label=key)
        # plt.xlabel('X-axis')
        # plt.ylabel('Y-axis')
        # plt.legend()
        # plt.show()

        # print("")


        estimations = mixins.denormalize(net.estimate(data_val, n_equipment), min_agg, max_agg)
        new_estimations_zeros = mixins.post_estimation_zeros(estimations, sts_val, n_equipment)
        saved_estimations = read_estimations_csv.read_estimations_csv(f"../../results/deep_learning/HIPE/1_week/estimated_active_power_{n_equipment}.csv")

        if idx == 0 and not os.path.exists("../../results/deep_learning/IMDELD/estimated_active_power.csv"):
            print(mixins.calculate_error(new_estimations_zeros, eq_val, n_equipment))
            save_csv.save_csv("../../results/deep_learning/IMDELD/estimated_active_power.csv", agg_val_denorm, new_estimations_zeros, timestamp)
        else:
            if (np.sum(mixins.calculate_error_different_zero(new_estimations_zeros, eq_val, sts_val, n_equipment)) / n_equipment) < (np.sum(mixins.calculate_error_different_zero(saved_estimations, eq_val, sts_val, n_equipment)) / n_equipment):
                print("--- Updating estimation ---")
                save_csv.save_csv("../../results/deep_learning/IMDELD/estimated_active_power.csv", agg_val_denorm, new_estimations_zeros, timestamp)


if __name__ == "__main__":
    main()

# %%
