import numpy as np
from typing import List

class NN:
    def __init__ (self) -> None:
        self.loss_fun = None
        self.loss_fun_d = None
        self.learning_rate = 0.1
        self.layers = []
        self.max_norm_eq = []
        self.epochs = 1000

    def set_loss(self, loss_fun: callable, loss_fun_d: callable) -> None:
        self.loss_fun = loss_fun
        self.loss_fun_d = loss_fun_d

    def set_layer(self, layer: object) -> None:
        self.layers.append(layer)

    def set_learning_rate(self, learning_rate: object) -> None:
        self.learning_rate = learning_rate

    def set_max_norm_eq(self, max_norm_eq: np.ndarray) -> None:
        self.max_norm_eq = max_norm_eq

    def set_epochs(self, epochs: int) -> None:
        self.epochs = epochs

    def train(self, inputs: np.ndarray, states: np.ndarray, aggs: np.ndarray) -> List[float]:
        print("Training network")

        loss_array = []

        for epoch in range(self.epochs):
            for input, agg in zip(inputs, aggs):
                # Forwards Propagation
                for layer in self.layers:
                    layer_output = layer.forw_prop(input)
                    input = layer_output
                loss = self.loss_fun_d(layer_output, agg, self.max_norm_eq)

                loss_array.append(self.loss_fun(layer_output, agg, self.max_norm_eq)[0, 0])

                # Backwards Propagation
                for layer in reversed(self.layers):
                    loss = layer.back_prop(self.learning_rate, loss)
        return loss_array

    def estimate(self, inputs: np.ndarray):
        print("Estimating values")
        output: np.ndarray = []
        results: np.ndarray = []
        for input in inputs:
            for layer in self.layers:
                output = layer.forw_prop(input)
                input = output
            results.append(output)
        return results
