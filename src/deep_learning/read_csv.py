import csv
import numpy as np


def read_csv(file_path: str, col_num: int = None) -> np.ndarray:
    with open(file_path, mode = 'r', encoding = 'utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Skip the first row
        if col_num is None:
            rows = [list(map(float, row[1:])) for row in reader]
        else:
            rows = [float(row[col_num]) for row in reader]    # Only read active power
    arr = np.array(rows)

    if col_num is not None:
        arr = arr.reshape(-1, 1)

    return arr
