import numpy as np

class NN:
    def __init__ (self) -> None:
        self.loss_fun = None
        self.loss_fun_d = None
        self.learning_rate = 0.1
        self.layers = []

    def set_loss(self, loss_fun: callable, loss_fun_d: callable) -> None:
        self.loss_fun = loss_fun
        self.loss_fun_d = loss_fun_d

    def set_layer(self, layer: object) -> None:
        self.layers.append(layer)

    def set_learning_rate(self, learning_rate: object) -> None:
        self.learning_rate = learning_rate

    def train(self, inputs: np.ndarray, outputs: np.ndarray, epochs: int) -> None:
        for x in range(epochs):
            for input, output in zip(inputs, outputs):
                # Forwards Propagation
                for layer in self.layers:
                    layer_output = layer.forw_prop(input)
                    input = layer_output
                loss = self.loss_fun_d(layer_output, output)
                # Backwards Propagation
                for layer in reversed(self.layers):
                    loss = layer.back_prop(self.learning_rate, loss)

    def estimate(self, inputs: np.ndarray):
        output: np.ndarray = []
        results: np.ndarray = []
        for input in inputs:
            for layer in self.layers:
                output = layer.forw_prop(input)
                input = output
            results.append(output)
        return results
