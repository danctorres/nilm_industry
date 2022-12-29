import csv
import os


def read_file(file_path):
    with open(file_path, 'r') as csv_file:
        lst = list(csv.DictReader(csv_file))
    return lst

def main():
    path = 'imdeld_dataset/Equipment'
    os.chdir(f"{path}")
    for file in os.listdir():
        if file.endswith('.csv'):
            lst_dic_csv = read_file(f'{file}')
            for x in range(len(lst_dic_csv)):
                print (lst_dic_csv[x])

if __name__ == "__main__":
    main()
