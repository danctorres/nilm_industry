import numpy as np

class Activation_layer():
    def __init__(self, activation: callable, activation_d: callable) -> None:
        super().__init__()
        self.activation = activation
        self.activation_d = activation_d

    def forw_prop(self, input: np.ndarray) ->np.ndarray:
        self.input = input
        self.output = self.activation(input)
        return self.output

    def back_prop(self, learning_rate: float, loss: np.ndarray) -> np.ndarray:
        return self.activation_d(self.input) * loss
