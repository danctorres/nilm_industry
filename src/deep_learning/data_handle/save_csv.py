import csv
import numpy as np
from typing import List


def save_csv(filename_path: str, agg_data: List[np.ndarray], eq_data: List[np.ndarray], list_timestamp: List[np.ndarray]) -> None:
    print("--- Saving into file ---")
    with open(filename_path, "w", newline="") as file:
        file.write("Timestamp, Aggregate_Active_Power, Estimates...\n")
        writer = csv.writer(file)
        for ag_array, eq_array, timestamp_array in zip(agg_data, eq_data, list_timestamp):
            writer.writerow(timestamp_array.flatten().tolist() + ag_array.flatten().tolist() + eq_array.flatten().tolist())
