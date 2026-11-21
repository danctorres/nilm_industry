%% ----------------------- DATASET PRE-PROCESSING ---------------------- %%
% Created by Daniel Torres
% Turns the raw HIPE one-week machine files into data/processed/HIPE/1_week.

close all; clear; clc;

% Methodology choices (values as used in the dissertation)
ON_THRESHOLD_KW = 0;        % a machine is ON when its power is > 0 kW, after clipping negatives, linear resampling to 1 s, spline synchronisation and rounding to 4 decimals
TRAINING_RATIO  = 0.7;      % share of each adaptive bin used for training, the rest for validation
% The aggregate written for N machines is the synthetic sum of those N machines, not the measured MainTerminal power.

rng(1);
root = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(fullfile(root, 'src', 'preprocessing'));
processed = fullfile(root, 'data', 'processed', 'HIPE', '1_week');


%% Read data
equip_data = read_equipment_csv(fullfile(root, 'data', 'raw', 'HIPE', 'Equipment'));
n_machines = numel(equip_data);


%% Parse timestamps, plot raw data, cut each machine at its first non-increasing timestamp and clip negative power
numRows = ceil(sqrt(n_machines));
numCols = ceil(n_machines / 4);

figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
eq_timetables = cell(1, n_machines);
for i = 1:n_machines
    Time = cellfun(@(x) x(1, 1:22), equip_data{i}.SensorDateTime, 'UniformOutput', false);
    Time = datetime(strrep(Time, '+', '.'), 'InputFormat', "yyyy-MM-dd'T'HH:mm:ss.SS");
    P_kW = equip_data{i}.P_kW;

    subplot(numRows, numCols, i);
    plot(Time, P_kW, '.');
    xlabel('Datestamp', 'FontSize', 20);
    ylabel('Active Power [kW]', 'FontSize', 13);
    title(sprintf('Equipment %d', i), 'FontSize', 20)

    stopIndex = find(diff(Time) <= 0, 1);
    if ~isempty(stopIndex)
        Time(stopIndex : end) = [];
        P_kW(stopIndex : end) = [];
    end
    P_kW(P_kW < 0.0) = 0.0;
    eq_timetables{i} = timetable(Time, P_kW);

    if (i == 1)
        start_time = Time(1);
        end_time = Time(end);
    else
        start_time = min(start_time, Time(1));
        end_time = max(end_time, Time(end));
    end
end


%% Processed equipment data
% Remove the first equipment since it is always OFF; columns keep the original equipment numbers
kept = 2:n_machines;
for i = kept
    eq_timetables{i} = retime(eq_timetables{i}, start_time:seconds(1):end_time, 'linear');
end
eq_processed_table_buff = timetable2table(synchronize(eq_timetables{kept}, 'union', 'spline'));
eq_processed_table = [eq_processed_table_buff(:, 1), array2table(round(eq_processed_table_buff{:, 2:end}, 4), 'VariableNames', cellstr("Eq" + kept + "_P_kW"))];
eq_processed_table.Properties.VariableNames{1} = 'Time';

ON_OFF_uint = uint8(eq_processed_table{:, 2:end} > ON_THRESHOLD_KW);
ON_OFF_table = [eq_processed_table(:, 1), array2table(ON_OFF_uint, 'VariableNames', cellstr("Eq" + kept + "_State"))];


%% Save data before splitting
aggregate_all = table(eq_processed_table.Time, sum(eq_processed_table{:, 2:end}, 2), 'VariableNames', {'Time', 'P_kW'});
writetable(ON_OFF_table, fullfile(processed, 'undivided', 'states.csv'));
writetable(eq_processed_table, fullfile(processed, 'undivided', 'equipment.csv'));
writetable(aggregate_all, fullfile(processed, 'undivided', 'aggregate.csv'));


%% Split into training and validation data for the first n kept machines and save into file
for n = 2:numel(kept)
    agg = table(eq_processed_table.Time, sum(eq_processed_table{:, 2:n + 1}, 2), 'VariableNames', {'Time', 'P_kW'});
    [training_index, validation_index] = split_train_validation(agg.P_kW, TRAINING_RATIO);

    writetable(agg(training_index, :), fullfile(processed, 'aggregate_training', sprintf('agg_training_%d.csv', n)));
    writetable(agg(validation_index, :), fullfile(processed, 'aggregate_validation', sprintf('agg_validation_%d.csv', n)));

    writetable(eq_processed_table(training_index, 1:n + 1), fullfile(processed, 'equipment_training', sprintf('eq_training_%d.csv', n)));
    writetable(eq_processed_table(validation_index, 1:n + 1), fullfile(processed, 'equipment_validation', sprintf('eq_validation_%d.csv', n)));

    writetable(ON_OFF_table(training_index, 1:n + 1), fullfile(processed, 'state_training', sprintf('st_training_%d.csv', n)));
    writetable(ON_OFF_table(validation_index, 1:n + 1), fullfile(processed, 'state_validation', sprintf('st_validation_%d.csv', n)));
end
