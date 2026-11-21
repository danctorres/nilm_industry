%% ----------------------- DATASET PRE-PROCESSING ---------------------- %%

% main.m
% Created by Daniel Torres on 12/09/2022 (MM-DD-YYYY)
% Turns the raw IMDELD files into data/processed/IMDELD/data_<N>_equipment.


%% ----------------------------- CORE CODE ----------------------------- %%
close all; clear; clc;

% Methodology choices (values as used in the dissertation)
ON_THRESHOLD_W      = 5;        % a machine is ON when its active power is > 5 W, one flat threshold for every machine
SMOOTHING_WINDOW    = 1500;     % movmean window in samples (1 s each, so 25 minutes) applied to machine and LVDB signals before spline interpolation
TRAINING_RATIO      = 0.7;      % share of each adaptive bin used for training, the rest for validation

rng(1);
root = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(fullfile(root, 'src', 'preprocessing'));
raw = fullfile(root, 'data', 'raw', 'IMDELD');


% Read the data from the equipment csv files (equipment index = alphabetical file order)
equip_data = read_equipment_csv(fullfile(raw, 'Equipment'));

% Identify common timestamps among equipment
selected_equipment_index = [1, 2, 3, 4, 7, 8];
common_timestamps = find_common_timestamps(equip_data, selected_equipment_index);

% Filter timestamps to obtain only those corresponding to days with relevant data
useful_common_timestamps = find_useful_timestamps(common_timestamps);

% Construct a table containing the timestamps and corresponding active power values for each piece of equipment
date_active_power = construct_date_unit_table(equip_data, useful_common_timestamps, 'active_power', selected_equipment_index);

% Delete NaN values
date_active_power = rmmissing(date_active_power);

% Interpolate the active power values to obtain a complete set of data the choosen days
metric_power_table      = calculate_metrics_power_day(date_active_power, selected_equipment_index);
active_power_formated   = interpolate_equipment_data(date_active_power, 'active_power', metric_power_table, selected_equipment_index, SMOOTHING_WINDOW);

% Compute the aggregate features from the LVDB-2 and LVDB-3
aggregate_formated_table = calculate_aggregate_all_feature(raw, active_power_formated.timestamp, selected_equipment_index, SMOOTHING_WINDOW);

% Calculate ON/OFF
on_off_array = calculate_on_off(active_power_formated, ON_THRESHOLD_W, selected_equipment_index);

% Split into training and validation and save final data
save_final_data(aggregate_formated_table, on_off_array, active_power_formated, selected_equipment_index, TRAINING_RATIO, ...
    fullfile(root, 'data', 'processed', 'IMDELD', sprintf('data_%d_equipment', numel(selected_equipment_index))));
