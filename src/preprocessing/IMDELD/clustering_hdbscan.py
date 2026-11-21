# Exploratory and unused by the pipeline: clusters histograms of data/interim/IMDELD/equipment_formated.csv into data/interim/IMDELD/hdbscan.
#%%
import csv
from pathlib import Path
import hdbscan
import numpy as np

INTERIM = Path(__file__).resolve().parents[3] / 'data' / 'interim' / 'IMDELD'

def read_file(file_path: str) -> list[dict[str, str]] :
    """Reads contents of csv file and save it to list of dictionaries"""
    with open(file_path, 'r', encoding = "utf-8") as csv_file:
        dic = list(csv.DictReader(csv_file))
    return dic


def clustering(points):
    clusterer = hdbscan.HDBSCAN()
    clusterer.fit(points)
    labels = clusterer.labels_
    return labels


def main() -> None:
    file_path = INTERIM / 'equipment_formated.csv'
    lst_dic_csv = read_file(f'{file_path}')
    list_keys = list(lst_dic_csv[0].keys())
    list_keys.remove('timestamp')

    for i, element in enumerate(list_keys):
        active_power_list = [ sub[element] for sub in lst_dic_csv ]
        hist, edges = np.histogram(np.array([float(x) for x in active_power_list]), bins='auto')
        bin_centers = (edges[:-1] + edges[1:]) / 2
        points = np.column_stack([bin_centers, hist])

        labels = clustering(points)

        np.savetxt(INTERIM / 'hdbscan' / f'histogram_eq{i + 1}.csv', np.column_stack([bin_centers, hist,  edges[:-1], edges[1:]]), delimiter=',', header='Bin Center, Frequency Count, Left Edges, Right Edges')
        np.savetxt(INTERIM / 'hdbscan' / f'labels_eq{i + 1}.csv', labels, delimiter=',', header='Cluster')
    print("done")


if __name__ == "__main__":
    main()


# %%
