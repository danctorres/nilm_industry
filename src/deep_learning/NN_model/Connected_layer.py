import numpy as np
from NN_model import Layer

class Connected_layer(Layer.Layer):
    def __init__(self, size_current: int, size_next: int) -> None:
        super().__init__()
        self.weights = np.random.uniform(low = -1.0, high = 1.0, size = (size_current, size_next))
        self.bias = np.random.uniform(low = -1.0, high = 1.0, size = (1, size_next))

    def forw_prop(self, input: np.ndarray) -> np.ndarray:
        self.input = input
        self.output = np.dot(input, self.weights) + self.bias
        return self.output

    def back_prop(self, learning_rate: float, loss: np.ndarray) -> np.ndarray:
        self.weights -= learning_rate * np.dot(self.input.T, loss)
        self.bias -= learning_rate * loss       # step size
        return np.dot(loss, self.weights.T)     # dE / d ouput
