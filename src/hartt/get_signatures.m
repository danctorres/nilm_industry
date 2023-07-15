close all; clear; clc;

%% Read training data
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
file_path_agg_train = [erase(file_dir, 'src\hartt'), 'data\processed\HIPE\1_week\aggregate_training\agg_training_9.csv'];
file_path_agg_val = [erase(file_dir, 'src\hartt'), 'data\processed\HIPE\1_week\aggregate_validation\agg_validation_9.csv'];
file_path_st_train = [erase(file_dir, 'src\hartt'), 'data\processed\HIPE\1_week\state_training\st_training_9.csv'];
file_path_st_val = [erase(file_dir, 'src\hartt'), 'data\processed\HIPE\1_week\state_validation\st_validation_9.csv'];


agg_train = readtable(file_path_agg_train);
agg_val = readtable(file_path_agg_val);
agg_table = vertcat(agg_train, agg_val);
agg_sort = sortrows(agg_table, 1);


st_train = readtable(file_path_st_train);
st_val = readtable(file_path_st_val);
st_table = vertcat(st_train, st_val);
st_sort = sortrows(st_table, 1);


clear file_information file_dir file_path_agg_train file_path_agg_val file_path_st_train file_path_st_val;
agg_train = sortrows(agg_train, 1);



agg_train_array = agg_train()
for i = 2:size(st_train, 2)
    diff_arr = diff(table2array(st_train(:, i)));
    change_indices = find(diff_arr ~= 0);
    differences = other_arr(change_indices + 1) - other_arr(change_indices);

    eq_consumption = 

end