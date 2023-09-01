# Created by danctorres

#%%
# import argparse
import os
# from typing import List
import numpy as np
# import matplotlib.pyplot as plt

from NN_model import Activation_layer
from NN_model import Connected_layer_batch
from NN_model import NN_batch
from NN_model import activation_function
from NN_model import loss_function
from data_handle import read_csv
from data_handle import save_csv
from data_handle import read_estimations_csv
from mixins import mixins


def read_eq_data(number_equipment: int):
    return read_csv.read_csv(f"../../data/processed/HIPE/1_week/equipment_training/eq_training_{number_equipment}.csv")

def read_train_data(number_equipment: int):
    print("--- Reading training data ---")
    sts_train = read_csv.read_csv(f"../../data/processed/HIPE/1_week/state_training/st_training_{number_equipment}.csv")
    agg_train_denorm = read_csv.read_csv(f"../../data/processed/HIPE/1_week/aggregate_training/agg_training_{number_equipment}.csv", 1)
    agg_train = mixins.normalize(agg_train_denorm)
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
    input_val = np.concatenate((sts_val, mixins.normalize(agg_val)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return mixins.normalize(agg_val), timestamp, eq_val, agg_val.min(), agg_val.max(), agg_val, sts_val


def read_undivided_data():
    print("--- Reading all agg data ---")
    sts_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/undivided/states.csv")
    agg_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/undivided/aggregate.csv", 1)
    timestamp = read_csv.read_csv(f"../../data/processed/HIPE/1_week/undivided/aggregate.csv", 0)
    eq_val = read_csv.read_csv(f"../../data/processed/HIPE/1_week/undivided/equipment.csv")
    input_val = np.concatenate((sts_val, mixins.normalize(agg_val)), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))
    return mixins.normalize(agg_val), timestamp, eq_val, agg_val.min(), agg_val.max(), agg_val, sts_val


def set_NN(n_equipment: int):
    net = NN_batch.NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer_batch.Connected_layer(1 + n_equipment, n_equipment + 2))
    net.set_layer(Activation_layer.Activation_layer(activation_function.relu, activation_function.relu_d))
    net.set_layer(Connected_layer_batch.Connected_layer(n_equipment + 2, n_equipment))
    net.set_layer(Activation_layer.Activation_layer(activation_function.tanh, activation_function.tanh_d))
    net.set_loss(loss_function.loss_f, loss_function.loss_f_d)
    net.set_epochs(1000)
    return net


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-n", "--number_eq", type=int, required=True, help="Number of equipment")
    # args = parser.parse_args()
    # n_equipment = args.number_eq

    for n_equipment in range(9, 10):
        number_runs = 100
        batch_size = 4
        old_loss = float('inf')

        print(f"Number of equipment: {n_equipment}")

        input_train, states_train, agg_train, min_agg, max_agg = read_train_data(n_equipment)
        agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm, sts_val = read_validation_data(n_equipment)
        data_val = np.concatenate ( (np.reshape(agg_val_norm, (agg_val_norm.shape[0], 1, 1)) , np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))), axis = 2)


        reshaped_agg_train = agg_train.reshape(-1, agg_train.shape[-1])
        batches_agg_train = np.array([reshaped_agg_train[i:i + batch_size] for i in range(0, len(reshaped_agg_train), batch_size)])
        reshaped_states_train = states_train.reshape(-1, states_train.shape[-1])
        batches_states_train = np.array([reshaped_states_train[i:i + batch_size] for i in range(0, len(reshaped_states_train), batch_size)])
        
        
        net_best = set_NN(n_equipment)
        net_best.set_batch_size = 4
        net_best.set_max_norm_eq(mixins.normalize2(np.max(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))
        net_best.set_min_norm_eq(mixins.normalize2(np.min(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))

        for idx in range(number_runs):
            print(f"Current iteration {idx}")
            net = set_NN(n_equipment)
            net.set_batch_size = 4
            net.set_max_norm_eq(mixins.normalize2(np.max(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))
            net.set_min_norm_eq(mixins.normalize2(np.min(read_eq_data(n_equipment), axis=0).reshape(1, n_equipment), min_agg, max_agg))
            loss_results = net.train(batches_agg_train, batches_states_train, n_equipment, True, False)

            # for key, value in loss_results.items():
            #     plt.plot(value, label=key)
            # plt.xlabel("X-axis")
            # plt.ylabel("Y-axis")
            # plt.legend()
            # plt.show()
            sum_loss = sum(loss_results[f"{0}"])
            print("")

            estimations = mixins.denormalize(net.estimate(data_val, n_equipment, False), min_agg, max_agg)
            new_estimations_zeros = mixins.post_estimation_zeros(estimations, sts_val, n_equipment)

            if idx == 0 and not os.path.exists(f"../../results/deep_learning/HIPE/1_week/states/estimated_active_power_{n_equipment}_9.csv"):
                net_best = net
                print(mixins.calculate_error(new_estimations_zeros, eq_val, n_equipment))
                save_csv.save_csv(f"../../results/deep_learning/HIPE/1_week/states/estimated_active_power_{n_equipment}_9.csv", agg_val_denorm, new_estimations_zeros, timestamp)
            else:
                saved_estimations = read_estimations_csv.read_estimations_csv(f"../../results/deep_learning/HIPE/1_week/states/estimated_active_power_{n_equipment}_9.csv")
                # if (np.sum(mixins.calculate_error_different_zero(new_estimations_zeros, eq_val, sts_val, n_equipment)) / n_equipment) < (np.sum(mixins.calculate_error_different_zero(saved_estimations, eq_val, sts_val, n_equipment)) / n_equipment):
                if (sum_loss < old_loss):
                    print("--- Updating estimation ---")
                    net_best = net
                    save_csv.save_csv(f"../../results/deep_learning/HIPE/1_week/states/estimated_active_power_{n_equipment}_9.csv", agg_val_denorm, new_estimations_zeros, timestamp)
            old_loss = sum_loss

    agg_val_norm, timestamp, eq_val, min_agg, max_agg, agg_val_denorm, sts_val = read_undivided_data()
    data_val = np.concatenate ( (np.reshape(agg_val_norm, (agg_val_norm.shape[0], 1, 1)) , np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))), axis = 2)
    estimations = mixins.denormalize(net_best.estimate(data_val, n_equipment, False), min_agg, max_agg)
    save_csv.save_csv(f"../../results/deep_learning/HIPE/1_week/states/estimated_active_power.csv", agg_val_denorm, estimations, timestamp)



if __name__ == "__main__":
    main()

# %%
