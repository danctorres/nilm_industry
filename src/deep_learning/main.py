import numpy as np

from Activation_layer import Activation_layer
from Connected_layer import Connected_layer
from NN import NN
from activation_function import activation, activation_d
from loss_function import loss, loss_d

x_train = np.array([[[0, 0]], [[0, 1]], [[1, 0]], [[1, 1]]])
y_train = np.array([[[0]], [[1]], [[0]], [[1]]])

net = NN()
net.set_learning_rate(0.1)
net.set_layer(Connected_layer(2, 5))
net.set_layer(Activation_layer(activation, activation_d))
net.set_layer(Connected_layer(5, 1))
net.set_layer(Activation_layer(activation, activation_d))

net.set_loss(loss, loss_d)
net.train(x_train, y_train, 1000)

out = net.estimate(x_train)
print(out)