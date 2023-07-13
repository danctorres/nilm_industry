import numpy as np
from typing import List

class NN:
    def __init__ (self) -> None:
        self.loss_fun = None
        self.loss_fun_d = None
        self.learning_rate = 0.1
        self.layers = []
        self.max_norm_eq = None
        self.min_norm_eq = None
        self.epochs = 1000
        self.threshold = 0.1

    def set_loss(self, loss_fun: callable, loss_fun_d: callable) -> None:
        self.loss_fun = loss_fun
        self.loss_fun_d = loss_fun_d

    def set_layer(self, layer: object) -> None:
        self.layers.append(layer)

    def set_learning_rate(self, learning_rate: object) -> None:
        self.learning_rate = learning_rate

    def set_max_norm_eq(self, max_norm_eq: np.ndarray) -> None:
        self.max_norm_eq = max_norm_eq

    def set_min_norm_eq(self, min_norm_eq: np.ndarray) -> None:
        self.min_norm_eq = min_norm_eq

    def set_epochs(self, epochs: int) -> None:
        self.epochs = epochs

    def set_threshold(self, threshold: float) -> None:
            self.threshold = threshold

    def train(self, aggs: np.ndarray, n_equipment: int): # -> Dict[List[float]]:
        loss_Dict = {f"{i}": [] for i in range(0, n_equipment + 1)}
        for epoch in range(self.epochs):
            for idx in range(aggs.shape[0]):
                if aggs[idx] != 0.0:
                    input_agg = aggs[idx]
                    # Forwards Propagation
                    for layer in self.layers:
                        layer_output = layer.forw_prop(input_agg)
                        input_agg = layer_output
                    loss = self.loss_fun_d(layer_output, aggs[idx], self.max_norm_eq, self.min_norm_eq, n_equipment)

                    # Backwards Propagation
                    for layer in reversed(self.layers):
                        loss = layer.back_prop(self.learning_rate, loss)

            print(f"Training network: {(epoch * 100) / (self.epochs - 1):.2f}% - Epoch: {epoch + 1}/{self.epochs}", end="\r")

            for index, value in np.ndenumerate(self.loss_fun(layer_output, aggs[aggs.shape[0] - 1], self.max_norm_eq, self.min_norm_eq, n_equipment)):
                loss_Dict[f"{index[1]}"].append(value)
        return loss_Dict

    def estimate(self, inputs: np.ndarray, n_equipment: int) -> List[np.ndarray]:
        print("--- Estimating values ---")
        output: np.ndarray = []
        results: np.ndarray = []
        for inp in inputs:
            if inp == 0.0:
                results.append(np.zeros((1, n_equipment)))
            else:
                for layer in self.layers:
                    output = layer.forw_prop(inp)
                    inp = output
                results.append(output)
        return results
