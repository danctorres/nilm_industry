import csv
import numpy as np
from typing import List


def read_estimations_csv(filename_path: str) -> List:
    print("--- Reading estimation file ---")
    data = []
    with open(filename_path, "r") as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for row in csvreader:
            array = np.array(row[2:], dtype=float)
            data.append(array.reshape(1, -1))
    return data
