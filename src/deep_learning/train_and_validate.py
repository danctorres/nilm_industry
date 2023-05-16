import numpy as np

from Activation_layer import Activation_layer
from Connected_layer import Connected_layer
from NN import NN
from activation_function import activation, activation_d
from loss_function import loss, loss_d
from read_csv import read_csv
from save_csv import save_csv

def main():
    # Read data for training
    sts_train = read_csv('../../data/processed/data_6_equipment/on_off_training.csv')
    agg_train_denormalized = read_csv('../../data/processed/data_6_equipment/aggregate_training.csv', 1)

    min_val = agg_train_denormalized.min()
    max_val = agg_train_denormalized.max()

    normalize = np.vectorize(lambda x: (x - min_val) / (max_val - min_val))
    agg_train = normalize(agg_train_denormalized)

    # Format data
    resh_sts_train = np.reshape(sts_train, (sts_train.shape[0], 1, sts_train.shape[1]))
    resh_agg_train = np.reshape(agg_train, (agg_train.shape[0], 1, agg_train.shape[1]))
    input_train = np.concatenate((sts_train, agg_train), axis = 1)
    resh_input_train = np.reshape(input_train, (input_train.shape[0], 1, input_train.shape[1]))
    eq_max_val = np.array([2000, 1500, 6000, 6000, 100000, 100000])


    net = NN()
    net.set_learning_rate(0.001)
    net.set_layer(Connected_layer(7, 7))
    net.set_layer(Activation_layer(activation, activation_d))
    net.set_layer(Connected_layer(7, 7))
    net.set_layer(Activation_layer(activation, activation_d))
    net.set_layer(Connected_layer(7, 6))
    net.set_layer(Activation_layer(activation, activation_d))
    net.set_loss(loss, loss_d)
    net.set_epochs(100000)

    net.set_max_norm_eq(normalize(eq_max_val))

    net.train(resh_input_train, resh_sts_train, resh_agg_train)


    # Read data for validation
    sts_val = read_csv('../../data/processed/data_6_equipment/on_off_validation.csv')
    agg_val_denormalized = read_csv('../../data/processed/data_6_equipment/aggregate_validation.csv', 1)

    min_val = agg_val_denormalized.min()
    max_val = agg_val_denormalized.max()
    print(min_val)
    print(max_val)
    agg_val = normalize(agg_val_denormalized)

    # Format data
    resh_sts_val = np.reshape(sts_val, (sts_val.shape[0], 1, sts_val.shape[1]))
    resh_agg_val = np.reshape(agg_val, (agg_val.shape[0], 1, agg_val.shape[1]))
    input_val= np.concatenate((sts_val, agg_val), axis = 1)
    resh_input_val = np.reshape(input_val, (input_val.shape[0], 1, input_val.shape[1]))

    out = net.estimate(resh_input_val)
    print(out)

    denormalize = np.vectorize(lambda x: x * (max_val - min_val) + min_val)
    denormalized_out = denormalize(out)
    # print(denormalized_out)

    save_csv('../../results/deep_learning/estimated_active_power.csv', denormalized_out)

if __name__ == '__main__':
    main()
