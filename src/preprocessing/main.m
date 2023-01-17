%% -------------- NILM dissertation dataset analysis code -------------- %%

% main.m
% By: Daniel Torres
% Created: 09/12/2022
% Updated: 09/01/2023



%% ----------------------------- CORE CODE ----------------------------- %%
close all; clear; clc;

% Make sure in correct path
file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));
clearvars file_ext file_name file_information
close all; clear; clc;


% Read the data from the equipment csv files
equip_data = read_equipment_csv(); % read dataset equipment csv, optional input (absolute path of equipment folder)


% Identify common timestamps among equipment
common_timestamps = find_common_timestamps(equip_data, 1:(size(equip_data, 2)));


% Filter timestamps to obtain only those corresponding to days with relevant data
useful_common_timestamps = find_useful_timestamps(common_timestamps);


% Construct a table containing the timestamps and corresponding active power values for each piece of equipment
date_active_power       = construct_date_unit_table(equip_data, useful_common_timestamps, 'active_power');
date_reactive_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'reactive_power');
date_apparent_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'apparent_power');
date_current            = construct_date_unit_table(equip_data, useful_common_timestamps, 'current');
date_voltage            = construct_date_unit_table(equip_data, useful_common_timestamps, 'voltage');


% Interpolate the active power values to obtain a complete set of data the choosen days
active_power_formated   = interpolate_equipment_data(date_active_power, 'active_power', true);
reactive_power_formated = interpolate_equipment_data(reactive_power, 'reactive_power', true);
apparent_power_formated = interpolate_equipment_data(date_apparent_power, 'apparent_power', true);
current_formated        = interpolate_equipment_data(date_current, 'current', true);
voltage_formated        = interpolate_equipment_data(date_voltage, 'voltage', true);


% Read and format data from 'pelletizer-subcircuit.csv' and 'millingmachine-subcircuit.csv'
lvdb2_table = read_lvdb_csv('active_power', 2, false);
lvdb3_table = read_lvdb_csv('active_power', 3, false);


% Compute the total power consumption  by summing LVDB2 and LVDB3
aggregate_table = calculate_aggregate(false, lvdb2_table, lvdb3_table);


% Correlation-based feature selection (CFS) to select features
R = select_feature([active_power_formated, reactive_power_formated, apparent_power_formated, current_formated, voltage_formated], aggregate_power);


% Histogram states for ON / OFF
[counts_cell, edges_cell, bin_center_cell, TF_cell] = histogram_without_outliers(equipment_formated, 2000, true, false);
[curves, params_normal, ~, group_power_limit] = get_params_normals(size(equipment_formated, 2) - 1, TF_cell, counts_cell, edges_cell, bin_center_cell);
histogram_state_peak_equipment(equipment_formated, group_power_limit)

% Calculate ON/OFF
on_off_array = calculate_on_off(equipment_formated, group_power_limit);


% Calculate power at the events for each equipment
power_events = estimate_power_events(aggregate_table, active_power_formated);



%% -------------------------- ADDITIONAL CODE -------------------------- %%

% Analyze the original data, active power, to find how many samples are not unique
[number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data);

% For the days that have information of the 8 equipment, find how many timestamps samples are missing
[day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps);

% Calculate the average power for each day
metric_power_table = calculate_metrics_power_day(date_active_power);

% Plot the histogram of each equipment power
histogram_equipment_original(equip_data, false);

% Plot the variables for the selected days before interpolation
plot_data_per_equipment(date_active_power, 'Active Power [W]', false);

% Plot the variables for the selected days after interpolation 
plot_data_selected_days(active_power_formated, 'Active Power [W]', false);
plot_data_selected_days(date_voltage, 'Voltage [V]', false);
plot_data_selected_days(date_current, 'Current [A]', false);

% Plot the variable for one day, by specifying what is the day index
plot_data_select_day(active_power_formated, 1, 'Active Power [W]', false);
plot_data_select_day(voltage_formated, 1, 'Voltage [V]', false);

% Plot histogram of the interpolated variables
histogram_equipment_formated(active_power_formated, false);

% Analyze the difference between the lvdb2, lvdb3 and agrgegate power
statistics_result_cell = statistical_diff_lvdb_aggregate(equipment_formated, lvdb2_table, lvdb3_table, aggregate_table, false);

% Function to convert and save a table as a json
% table_2_json();



%% --------------------- Currently in development ---------------------- %%



% Remove outliers
% figure;
% for i = 1:size(equipment_formated, 2) - 1
%     x_clean = rmoutliers(table2array(equipment_formated(:, i + 1)), 'mean', 'ThresholdFactor', 3);
%     subplot((size(equipment_formated, 2) - 1) / 2, 2, i);
%     plot(x_clean)
% end

% read csv
file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\hdbscan']);

file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end);



equip_data = cell(1, size(file_list, 2));
for i = 1:size(file_list, 2)
    equip_data{i} = readtable(string(file_list(i)));
end


ht_1 = readtable("histogram_eq7.csv");
lt_1 = readtable("labels_eq7.csv");
edges = [ht_1.LeftEdges; ht_1.RightEdges(end)]';
counts = ht_1.FrequencyCount';
h = histogram('BinEdges', edges,'BinCounts', counts);
hold on
scatter(ht_1.x_BinCenter, counts, 20, lt_1.x_Cluster);

for i = 1:size(counts, 2)
    set(bars(i), 'FaceColor', colors{i,1});
end

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));



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
mbeautify_path = [erase(file_information.Filename, ['dissertation_nilm\src\preprocessing\', file_name, file_ext]), '\MBeautifier\'];
cd(mbeautify_path);
source_folder = ([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\src\preprocessing\']);
% mbeautify_path = [erase(file_information.Filename, ['\dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
% cd(mbeautify_path);
% files_names = file_list(endsWith(file_list, 'm'));
% for i = 1:size(files_names, 2)
%     MBeautify.formatFile([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\', files_names{i}]);
% end
 