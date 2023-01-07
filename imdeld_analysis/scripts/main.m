%% %%%%%%%%%%%%%% NILM dissertation dataset analysis code %%%%%%%%%%%%%% %%
% Daniel Torres
% 09/12/2022



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% CORE CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%% %%
close all; clear; clc;

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));
clearvars file_ext file_name file_information

% Read the data from the equipment csv files
equip_data = read_equipment_csv(); % read dataset equipment csv

% Identify common timestamps among equipment
common_timestamps = find_common_timestamps(equip_data);

% Filter timestamps to obtain only those corresponding to days with relevant data
useful_common_timestamps = find_useful_timestamps(common_timestamps);

% Construct a table containing the timestamps and corresponding active power values for each piece of equipment
date_active_power = construct_date_power_table(equip_data, useful_common_timestamps);

% Interpolate the active power values to obtain a complete set of data the choosen days
equipment_formated = interpolate_equipment_data(date_active_power, false);

% Read and format data from 'pelletizer-subcircuit.csv' and 'millingmachine-subcircuit.csv'
lvdb2_table = read_lvdb2_csv(false);
lvdb3_table = read_lvdb3_csv(false);

% Compute the total power consumption  by summing LVDB2 and LVDB3
aggregate_table = calculate_aggregate(false, lvdb2_table, lvdb3_table);



%% %%%%%%%%%%%%%%%%%%%%%%%%%% ADDITIONAL CODE %%%%%%%%%%%%%%%%%%%%%%%%%% %%
[number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data);
[day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps);
average_power_day = calculate_average_power_day(date_active_power);
histogram_equipment_original(equip_data, false);
plot_active_power_per_day(date_active_power, false);
plot_power_selected_days(equipment_formated, false);
histogram_equipment_formated(equipment_formated, false);
statistics_result_cell = statistical_diff_lvdb_aggregate(equipment_formated, lvdb2_table, lvdb3_table, aggregate_table, false);

% table_2_json(); % Convert a table and save it has a json


%% %%%%%%%%%%%%%%%% Currently in development



%%%%%%%%%%%%%%%%%%%% %% Linting and Indentation tool %% %%%%%%%%%%%%%%%%%%%%
close all;  clc;

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));

file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end); % remove . and ..

checkcode(file_list(endsWith(file_list, 'm')))

% Indentation tool
% git clone github.com/davidvarga/MBeautifier into the same path level that dissertation_nilm
mbeautify_path = [erase(file_information.Filename, ['dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
cd(mbeautify_path);
source_folder = ([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\']);

% mbeautify_path = [erase(file_information.Filename, ['\dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
% cd(mbeautify_path);
% files_names = file_list(endsWith(file_list, 'm'));
% for i = 1:size(files_names, 2)
%     MBeautify.formatFile([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\', files_names{i}]);
% end
 