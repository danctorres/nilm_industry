# import csv
#
# # Specify the input and output file paths
# sts_train = '../../data/processed/HIPE/1_week/on_off_training.csv'
# sts_val = '../../data/processed/HIPE/1_week/on_off_validation.csv'
#
# eq_train = '../../data/processed/HIPE/1_week/equipment_training.csv'
# eq_val = '../../data/processed/HIPE/1_week/equipment_validation.csv'
#
#
# input_file = eq_val
# output_file = eq_val
#
# # Specify the column index to be deleted (0-based index)
# column_index_to_delete = 1
#
# # Read the input CSV file
# with open(input_file, 'r') as file:
#     reader = csv.reader(file)
#     rows = [row for row in reader]
#
# # Remove the column from each row
# for row in rows:
#     del row[column_index_to_delete]
#
# # Write the updated data to the output CSV file
# with open(output_file, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(rows)
#
# print("Column successfully deleted from the CSV file.")