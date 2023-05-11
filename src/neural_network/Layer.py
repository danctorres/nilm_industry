import numpy as np

class Layer:
    def __init__(self) -> None:
        self.input = None
        self.output = None

    def forw_prop(self, input):
        pass

    def back_prop(self, error: np.ndarray, learning_rate: float) -> np.ndarray:
        pass
