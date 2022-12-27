import csv
import os


def read_text_file(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            var_key = row['key']
            var_value = row['value']
            data[var_key] = var_value
        return data

def main():
    path = 'imdeld_dataset/Equipment'
    os.chdir(f"{path}")
    print(os.getcwd())
    for file in os.listdir():
        if file.endswith('.csv'):
            dic = read_text_file(f'{file}')
            print(dic.keys())

if __name__ == "__main__":
    main()
