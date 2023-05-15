import numpy as np


def save_csv(filename: str, array: np.array) -> None:
    print("Saving into file")
    array_reshaped = np.reshape(array, (-1, array.shape[-1]))
    np.savetxt(filename, array_reshaped, delimiter=',')
