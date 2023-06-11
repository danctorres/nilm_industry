import csv
import numpy as np
from typing import List


def save_csv(filename_path: str, list_data: List[np.ndarray], list_timestamp: List[np.ndarray]) -> None:
    print("Saving into file")
    with open(filename_path, 'w', newline='') as file:
        file.write("Timestamp, Aggregate_Active_Power, Estimate_0, Estimate_1, Estimate_2, Estimate_3, Estimate_4, Estimate_5\n")
        writer = csv.writer(file)
        for data_array, timestamp_array in zip(list_data, list_timestamp):
            row = timestamp_array.flatten().tolist()
            writer.writerow(row + data_array.flatten().tolist())
