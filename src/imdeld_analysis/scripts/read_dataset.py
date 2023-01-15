"""Module for reading csv and path functions."""
import csv
import os


def read_file(file_path: str) -> list[dict[str, str]] :
    """Reads contents of csv file and save it to list of dictionaries"""
    with open(file_path, 'r', encoding = "utf-8") as csv_file:
        lst = list(csv.DictReader(csv_file))
    return lst

def main() -> None:
    """Testing"""
    path = 'imdeld_dataset/Equipment'
    os.chdir(f"{path}")
    for file in os.listdir():
        if file.endswith('.csv'):
            lst_dic_csv = read_file(f'{file}')
            # for index in enumerate(lst_dic_csv):
            #     print (lst_dic_csv[index])

if __name__ == "__main__":
    main()
