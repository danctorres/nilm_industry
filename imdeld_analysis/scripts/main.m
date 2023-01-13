%% -------------- NILM dissertation dataset analysis code -------------- %%

% main.m
% By: Daniel Torres
% Created: 09/12/2022
% Updated: 09/01/2023



%% ----------------------------- CORE CODE ----------------------------- %%
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
date_active_power       = construct_date_unit_table(equip_data, useful_common_timestamps, 'active_power');
date_reactive_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'reactive_power');
date_apparent_power     = construct_date_unit_table(equip_data, useful_common_timestamps, 'apparent_power');
date_current            = construct_date_unit_table(equip_data, useful_common_timestamps, 'current');
date_voltage            = construct_date_unit_table(equip_data, useful_common_timestamps, 'voltage');


% Interpolate the active power values to obtain a complete set of data the choosen days
active_power_formated   = interpolate_equipment_data(date_active_power, false);
reactive_power_formated = interpolate_equipment_data(reactive_power, false);
apparent_power_formated = interpolate_equipment_data(date_apparent_power, false);
voltage_formated        = interpolate_equipment_data(date_voltage, false);
current_formated        = interpolate_equipment_data(date_current, false);


% Read and format data from 'pelletizer-subcircuit.csv' and 'millingmachine-subcircuit.csv'
lvdb2_table = read_lvdb2_csv(false);
lvdb3_table = read_lvdb3_csv(false);

% Compute the total power consumption  by summing LVDB2 and LVDB3
aggregate_table = calculate_aggregate(false, lvdb2_table, lvdb3_table);


% Histogram states
[counts_cell, edges_cell, bin_center_cell, TF_cell] = histogram_without_outliers(equipment_formated, 2000, true, false);
[curves, params_normal, ~, group_power_limit] = get_params_normals(size(equipment_formated, 2) - 1, TF_cell, counts_cell, edges_cell, bin_center_cell);
histogram_state_peak_equipment(equipment_formated, group_power_limit)

% Calculate ON/OFF
on_off_array = calculate_on_off(equipment_formated, group_power_limit);

% Calculate power at the events for each equipment




%% -------------------------- ADDITIONAL CODE -------------------------- %%
[number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data);
[day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps);
average_power_day = calculate_average_power_day(date_active_power);
histogram_equipment_original(equip_data, false);

plot_data_per_equipment(date_active_power, 'Active Power [W]', false);
plot_data_per_equipment(date_voltage, 'Voltage [V]', false);
plot_data_per_equipment(date_current, 'Current [A]', false);


plot_data_selected_days(active_power_formated, 'Active Power [W]', false);

plot_data_select_day(equipment_formated, 1, 'Active Power [W]', false);
plot_data_select_day(voltage_formated, false, 'Voltage [V]', false);

histogram_equipment_formated(equipment_formated, false);

statistics_result_cell = statistical_diff_lvdb_aggregate(equipment_formated, lvdb2_table, lvdb3_table, aggregate_table, false);

% table_2_json(); % Convert a table and save it has a json



%% --------------------- Currently in development ---------------------- %%
aggregate_array = table2array(aggregate_table(:, 2));
events_index = logical(zeros(size(equipment_formated, 1), size(equipment_formated, 2) - 1));
aggregate_array_clean = rmoutliers(aggregate_array(:, 1), 'mean', 'ThresholdFactor', 3);
figure,
for i = 1:size(equipment_formated, 2) - 1
    events_index(:, i) = logical([diff(on_off_array(:, i)) ~= 0; 0]);
    %power_events(:, i) = {abs(diff(aggregate_array_clean(events_index(:, i))))};
    power_events(:, i) = {abs(diff(aggregate_array(events_index(:, i))))};
    subplot((size(equipment_formated, 2) - 1) / 2, 2, i)
    power_events_clean = rmoutliers(cell2mat(power_events(:, i)), 'mean', 'ThresholdFactor', 3);
    plot(power_events{i}, '.');
    % histogram(power_events_clean, 100)
    % histogram(power_events{i}, 100);

    c = polyfit(1:size(power_events{i}, 1), power_events{i}, 1);
    y_est = polyval(c, 1:size(power_events{i}, 1));
    hold on
    plot(1:size(power_events{i}, 1), y_est, 'r--', 'LineWidth', 2)

end


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
mbeautify_path = [erase(file_information.Filename, ['dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
cd(mbeautify_path);
source_folder = ([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\']);
% mbeautify_path = [erase(file_information.Filename, ['\dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
% cd(mbeautify_path);
% files_names = file_list(endsWith(file_list, 'm'));
% for i = 1:size(files_names, 2)
%     MBeautify.formatFile([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\', files_names{i}]);
% end
 