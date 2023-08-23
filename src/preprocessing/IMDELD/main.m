%% ----------------------- DATASET PRE-PROCESSING ---------------------- %%

% main.m
% Created by Daniel Torres on 12/09/2022 (MM-DD-YYYY)


%% ----------------------------- CORE CODE ----------------------------- %%
close all; clear; clc;

% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd(file_dir);
clearvars file_dir file_information
close all; clear; clc;


% Read the data from the equipment csv files
equip_data = read_equipment_csv('IMDELD'); % read dataset equipment csv, optional input (absolute path of equipment folder)

% Identify common timestamps among equipment
selected_equipment_index = [1, 2, 3, 4, 7, 8];
common_timestamps = find_common_timestamps(equip_data, selected_equipment_index);

% Filter timestamps to obtain only those corresponding to days with relevant data
useful_common_timestamps = find_useful_timestamps(common_timestamps);

% Construct a table containing the timestamps and corresponding active power values for each piece of equipment
date_active_power       = construct_date_unit_table(equip_data, useful_common_timestamps, 'active_power', selected_equipment_index);
date_reactive_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'reactive_power', selected_equipment_index);
date_apparent_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'apparent_power', selected_equipment_index);
date_current            = construct_date_unit_table(equip_data, useful_common_timestamps, 'current', selected_equipment_index);
date_voltage            = construct_date_unit_table(equip_data, useful_common_timestamps, 'voltage', selected_equipment_index);


% Delete NaN values
date_active_power       = rmmissing(date_active_power);
date_reactive_power     = rmmissing(date_reactive_power);
date_apparent_power     = rmmissing(date_apparent_power);
date_current            = rmmissing(date_current);
date_voltage            = rmmissing(date_voltage);


% Interpolate the active power values to obtain a complete set of data the choosen days
metric_power_table      = calculate_metrics_power_day(date_active_power, selected_equipment_index);

active_power_formated   = interpolate_equipment_data(date_active_power, 'active_power', metric_power_table, selected_equipment_index, false);
reactive_power_formated = interpolate_equipment_data(date_reactive_power, 'reactive_power', metric_power_table, selected_equipment_index, false);
apparent_power_formated = interpolate_equipment_data(date_apparent_power, 'apparent_power', metric_power_table, selected_equipment_index, false);
current_formated        = interpolate_equipment_data(date_current, 'current', metric_power_table, selected_equipment_index, false);
voltage_formated        = interpolate_equipment_data(date_voltage, 'voltage', metric_power_table, selected_equipment_index, false);


% Compute the total power consumption from the LVDB-2 and LVDB-3
aggregate_formated_table = calculate_aggregate_all_feature(active_power_formated.timestamp, selected_equipment_index, false);

% Calculate ON/OFF
on_off_array = calculate_on_off(active_power_formated, 5, false);

% Save final data
[aggregate_training, equipment_training, on_off_training, aggregate_validation, equipment_validation, on_off_validation] = save_final_data(aggregate_formated_table, on_off_array, active_power_formated, 0.7, true);


%-------------------------- VISUALIZATION CODE --------------------------%
% Analyze the original data, active power, to find how many samples are not unique
[number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data);

% Plot raw data for each equipment
plot_raw_active_power(equip_data, 'active_power');

% For the days that have information of the 8 equipment, find how many timestamps samples are missing
[day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps);

% Calculate the average power for each day
metric_power_table = calculate_metrics_power_day(date_active_power);

% Plot the histogram of each equipment power
histogram_equipment_original(equip_data, false);

% Plot the variables for the selected days before interpolation
plot_data_per_equipment(date_active_power, 'Active Power [W]', false);          % before interpolation
plot_data_per_equipment(active_power_formated, 'Active Power [W]', false);      % after interpolation


% Plot the variables for the selected days after interpolation
plot_data_selected_days(active_power_formated, 'Active Power [W]', false);
plot_data_selected_days(reactive_power_formated, 'Reactive Power [VAR]', false);
plot_data_selected_days(apparent_power_formated, 'Apparent Power [VA]', false);
plot_data_selected_days(voltage_formated, 'Voltage [V]', false);
plot_data_selected_days(current_formated, 'Current [A]', false);

% Plot the variable for one day, by specifying what is the day index
plot_data_select_day(active_power_formated, 1, 'Active Power [W]', false);
plot_data_select_day(voltage_formated, 1, 'Voltage [V]', false);
plot_data_select_day(aggregate_power, 1, 'Active Power [W]', false);


% Plot aggregate features vs individual equipment active power
plot_aggregate_vs_equipment(aggregate_formated_table, active_power_formated);
plot_aggregate_vs_equipment(aggregate_training, equipment_training);



%--------------------------- EXTRAS CORE CODE ---------------------------%
% Calculate power at the events for each equipment
power_events = estimate_power_events(aggregate_active_power, on_off_array);

% Plot histogram of the interpolated variables
histogram_equipment_formated(active_power_formated, false);

% Analyze the difference between the lvdb2, lvdb3 and agrgegate power
statistics_result_cell = statistical_diff_lvdb_aggregate(active_power_formated, lvdb2_table, lvdb3_table, aggregate_power, true);


% Correlation-based feature selection (CFS) to select features
power_factor = calculate_PF(active_power_formated, apparent_power_formated, selected_equipment_index);
[R_per_eq, R_per_unit, features_per_eq_sorted, features_unit_sorted] = select_feature(aggregate_power.active_power, [active_power_formated(:, 2:end), reactive_power_formated(:, 2:end), apparent_power_formated(:, 2:end), current_formated(:, 2:end), voltage_formated(:, 2:end), power_factor(:, 2:end)]);

aggregate_correlation = calculate_corr(aggregate_formated_table);

corr = calculate_corr_aggregate_eq(aggregate_formated_table, active_power_formated);

% Histogram states for ON / OFF
[counts_cell, edges_cell, bin_center_cell, TF_cell] = histogram_without_outliers(active_power_formated, 2000, true, false);
[curves, params_normal, ~, group_power_limit]       = get_params_normals(size(active_power_formated, 2) - 1, TF_cell, counts_cell, edges_cell, bin_center_cell);
histogram_state_peak_equipment(active_power_formated, group_power_limit)


% read csv from iterim dataset
% active_power_formated = read_interim_data('active_power_formated.csv');



%% ------------------- Linting and Indentation tool -------------------- %%
close all;  clc;

% Linting
file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));
file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end);
checkcode(file_list(endsWith(file_list, 'm')))

% Indentation tool
% git clone github.com/davidvarga/MBeautifier into the same path level that dissertation_nilm
mbeautify_path = [erase(file_information.Filename, ['dissertation_nilm\src\preprocessing\IMDELD\', file_name, file_ext]), '\MBeautifier\'];
cd(mbeautify_path);
source_folder = ([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\src\preprocessing\IMDELD\']);
% mbeautify_path = [erase(file_information.Filename, ['\dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
% cd(mbeautify_path);
% files_names = file_list(endsWith(file_list, 'm'));
% for i = 1:size(files_names, 2)
%     MBeautify.formatFile([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\', files_names{i}]);
% end
