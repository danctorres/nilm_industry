%% ----------------------- DATASET PRE-PROCESSING ---------------------- %%
% Created by Daniel Torres

close all; clear; clc;

%% Read data
% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd([erase(file_dir, 'HIPE'), 'IMDELD']);

equip_data = read_equipment_csv('HIPE');

cd(file_dir);
agg_data = read_aggregate('HIPE');
clearvars file_dir file_information


%% Processed equipment data
numRows = ceil(sqrt(size(equip_data, 2)));
numCols = ceil(size(equip_data, 2) / 4);

figure,
clear eq_cell;
for i = 1 : size(equip_data, 2)
   eq_cell{i} = equip_data{i}(:, {'SensorDateTime', 'P_kW'});
   subplot(numRows, numCols, i);
   plot(eq_cell{i}.P_kW);
end

for i = 1 : size(equip_data, 2)
    eq_buff = eq_cell{i};
    eq_buff.Properties.VariableNames{'SensorDateTime'} = 'Time';
    eq_buff.Time = cellfun(@(x) x(1, 1:22), eq_buff.Time, 'UniformOutput', false);
    eq_buff.Time = strrep(eq_buff.Time, '+', '.');
    eq_buff.Time = datetime(eq_buff.Time, 'InputFormat',"yyyy-MM-dd'T'HH:mm:ss.SS");
    
    stopIndex = find(diff(eq_buff.Time) <= 0, 1);
    if stopIndex > 0
        eq_buff(stopIndex : end, :) = [];
    end

    eq_buff.P_kW(eq_buff.P_kW < 0.0) = 0.0;
    if (i == 1)
        start_time = eq_buff.Time(1);
        end_time = eq_buff.Time(end);
    else
        if (start_time > eq_buff.Time(1))
            start_time = eq_buff.Time(1);
        end
        if (end_time < eq_buff.Time(end))
            end_time = eq_buff.Time(end);
        end
    end
    clear stopIndex eq_buff;
end

eq_processed_timetable = {};
for i = 1 : size(equip_data, 2)
    eq_buff = eq_cell{i};
    eq_buff.Properties.VariableNames{'SensorDateTime'} = 'Time';
    eq_buff.Time = cellfun(@(x) x(1, 1:22), eq_buff.Time, 'UniformOutput', false);
    eq_buff.Time = strrep(eq_buff.Time, '+', '.');
    eq_buff.Time = datetime(eq_buff.Time, 'InputFormat',"yyyy-MM-dd'T'HH:mm:ss.SS");
    
    stopIndex = find(diff(eq_buff.Time) <= 0, 1);
    if stopIndex > 0
        eq_buff(stopIndex : end, :) = [];
    end

    eq_buff.P_kW(eq_buff.P_kW < 0.0) = 0.0;
    eq_processed_timetable{i} = retime(timetable(eq_buff.Time, eq_buff.P_kW), start_time:seconds(1):end_time, 'linear');
    clear stopIndex eq_buff;
end

% Remove data from first equipment since it is always OFF
eq_processed_timetable = eq_processed_timetable(1:numel(eq_processed_timetable) ~= 1);

eq_processed_table_buff = timetable2table(synchronize(eq_processed_timetable{:}, 'union', 'spline'));
eq_processed_table = [eq_processed_table_buff(:, 1), array2table( round(table2array(eq_processed_table_buff(:, 2:end)), 4 ))];
eq_processed_table.Properties.VariableNames{'Var1'} = 'Eq1_P_kW';
eq_processed_table.Properties.VariableNames{'Var2'} = 'Eq2_P_kW';
eq_processed_table.Properties.VariableNames{'Var3'} = 'Eq3_P_kW';
eq_processed_table.Properties.VariableNames{'Var4'} = 'Eq4_P_kW';
eq_processed_table.Properties.VariableNames{'Var5'} = 'Eq5_P_kW';
eq_processed_table.Properties.VariableNames{'Var6'} = 'Eq6_P_kW';
eq_processed_table.Properties.VariableNames{'Var7'} = 'Eq7_P_kW';
eq_processed_table.Properties.VariableNames{'Var8'} = 'Eq8_P_kW';
eq_processed_table.Properties.VariableNames{'Var9'} = 'Eq9_P_kW';
clear equip_data eq_processed_timetable eq_cell start_time end_time;

ON_OFF_double = table2array(eq_processed_table(:, 2:end));
ON_OFF_double(ON_OFF_double > 0) = 1;
ON_OFF_double(ON_OFF_double < 0) = 0;
ON_OFF_uint = uint8(ON_OFF_double);
clear ON_OFF_double eq_processed_table_buff;

figure,
for i = 1 : size(ON_OFF_uint, 2)
    subplot(numRows, numCols, i);
    plot(ON_OFF_uint(:, i));
end

column_names = string(eq_processed_table.Properties.VariableNames);
ON_OFF_table = array2table(ON_OFF_uint, 'VariableNames', column_names(2:end));
ON_OFF_table = addvars(ON_OFF_table, eq_processed_table.Time, 'Before', 1, 'NewVariableNames', 'Time');
ON_OFF_table.Properties.VariableNames = {'Time', 'Eq1_State', 'Eq2_State', 'Eq3_State', 'Eq4_State', 'Eq5_State', 'Eq6_State', 'Eq7_State', 'Eq8_State', 'Eq9_State'};

clear  numCols numRows column_names ON_OFF_uint i;


%% Processed aggregate data
% agg_power_data = agg_data(:, {'SensorDateTime', 'P_kW'});
% agg_power_data.SensorDateTime = cellfun(@(x) x(1, 1:22), agg_power_data.SensorDateTime, 'UniformOutput', false);
% agg_power_data.SensorDateTime = strrep(agg_power_data.SensorDateTime, '+', '.');
% agg_power_data.SensorDateTime = datetime(agg_power_data.SensorDateTime, 'InputFormat',"yyyy-MM-dd'T'HH:mm:ss.SS");
% 
% stopIndex = find(diff(agg_power_data.SensorDateTime) <= 0, 1);
% if stopIndex > 0
%     agg_power_data(stopIndex : end, :) = [];
% end
% clear stopIndex;
% agg_interpolated_table = retime(timetable(agg_power_data.SensorDateTime, agg_power_data.P_kW), start_time:seconds(1):end_time, 'linear');
% 
% aggregate_table = timetable2table(synchronize(timetable(eq_processed_table.Time, eq_processed_table.Eq1_P_kW), agg_interpolated_table, 'union', 'spline'));
% aggregate_table = removevars(aggregate_table, "Var1_1");
% aggregate_table.Properties.VariableNames{'Var1_agg_interpolated_table'} = 'Agg_P_kW';

% Synthetic aggregate values = sum of equipment values
for i = 2:size(eq_processed_table, 2) - 1
    agg_struct_of_tables.(sprintf('aggregate_table_%d', i)) = table(eq_processed_table.Time, sum(eq_processed_table{:, 2 : i + 1}, 2), 'VariableNames', {'Time', 'P_kW'});
end
clear i agg_buff agg_data;

figure,
plot(agg_struct_of_tables.aggregate_table_9.P_kW)


%% Split into training and validation data and save into file
relativeFolderPath = '../../../data/processed/HIPE/1_week/';

training_ratio = 0.7;
table_names = fieldnames(agg_struct_of_tables);
for i = 1:size(table_names, 1)
    timestamps      = agg_struct_of_tables.(table_names{i}).Time;
    agg_buff        = agg_struct_of_tables.(table_names{i}).P_kW;
    mean_aggregate  = mean(agg_buff);
    std_aggregate   = std(agg_buff);
    bin_edges       = mean_aggregate + [-3 * std_aggregate, -2 * std_aggregate, -1 * std_aggregate, 0, 1 * std_aggregate, 2 * std_aggregate, 3 * std_aggregate];
    [N, ~, bin]     = histcounts(agg_buff, bin_edges);
    buffer          = 1:1:(size(agg_buff, 1) - 1);
    unique_bins     = intersect(buffer(N > 100), unique(bin));
    n_samples_bin   = 1000 * training_ratio;

    for j = 1:size(unique_bins, 1)
        bin_samples = find(bin == unique_bins(j));
        if (n_samples_bin > size(bin_samples, 1))
            n_samples_bin = size(bin_samples, 1);
        end
    end

    n_samples_bin = floor(n_samples_bin * training_ratio);
    training_index      = [];
    validation_index    = [];
    for j = 1:size(unique_bins, 1)
        bin_samples             = find(bin == unique_bins(j));
        bin_index_training      = randsample(bin_samples, n_samples_bin);
        bin_index_validation    = randsample(setdiff(bin_samples, bin_index_training), floor(n_samples_bin * (1 - training_ratio)));
        training_index          = [training_index; bin_index_training];
        validation_index        = [validation_index; bin_index_validation];
    end
    training_index = reshape(training_index(randperm(numel(training_index))), size(training_index));
    validation_index = reshape(validation_index(randperm(numel(validation_index))), size(validation_index));

    agg_training.(sprintf('aggregate_table_%d', i + 1))             = array2table(timestamps(training_index, :), 'VariableNames', {'Time'});
    agg_training.(sprintf('aggregate_table_%d', i + 1)).P_kW        = agg_buff(training_index, :);

    agg_validation.(sprintf('aggregate_table_%d', i + 1))           = array2table(timestamps(validation_index, :), 'VariableNames', {'Time'});
    agg_validation.(sprintf('aggregate_table_%d', i + 1)).P_kW      = agg_buff(validation_index, :);

    eq_training.(sprintf('equipment_table_%d', i + 1))              = eq_processed_table(training_index, 1 : i + 2);
    eq_validation.(sprintf('equipment_table_%d', i + 1))            = eq_processed_table(validation_index, 1 : i + 2);

    st_training.(sprintf('state_table_%d', i + 1))                  = ON_OFF_table(training_index, 1 : i + 2);
    st_validation.(sprintf('state_table_%d', i + 1))                = ON_OFF_table(validation_index, 1 : i + 2);

    writetable(agg_training.(sprintf('aggregate_table_%d', i + 1)), fullfile([relativeFolderPath, 'aggregate_training/'], sprintf('agg_training_%d.csv', i + 1)));
    writetable(agg_validation.(sprintf('aggregate_table_%d', i + 1)), fullfile([relativeFolderPath, 'aggregate_validation/'], sprintf('agg_validation_%d.csv', i + 1)));

    writetable(eq_training.(sprintf('equipment_table_%d', i + 1)), fullfile([relativeFolderPath, 'equipment_training/'], sprintf('eq_training_%d.csv', i + 1)));
    writetable(eq_training.(sprintf('equipment_table_%d', i + 1)), fullfile([relativeFolderPath, 'equipment_validation/'], sprintf('eq_validation_%d.csv', i + 1)));

    writetable(st_training.(sprintf('state_table_%d', i + 1)), fullfile([relativeFolderPath, 'state_training/'], sprintf('st_training_%d.csv', i + 1)));
    writetable(st_validation.(sprintf('state_table_%d', i + 1)), fullfile([relativeFolderPath, 'state_validation/'], sprintf('st_validation_%d.csv', i + 1)));
end

clear training_index validation_index bin_index_validation bin_index_training bin_samples i j n_samples_bin unique_bins buffer N bin bin_edges std_aggregate mean_aggregate agg_buff timestamps table_names training_ratio relativeFolderPath;
