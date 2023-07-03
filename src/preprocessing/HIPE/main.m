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

eq_processed_table = timetable2table(synchronize(eq_processed_timetable{:}, 'union', 'spline'));
eq_processed_table.Properties.VariableNames{'Var1_1'} = 'Eq1_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_2'} = 'Eq2_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_3'} = 'Eq3_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_4'} = 'Eq4_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_5'} = 'Eq5_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_6'} = 'Eq6_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_7'} = 'Eq7_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_8'} = 'Eq8_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_9'} = 'Eq9_P_kW';
eq_processed_table.Properties.VariableNames{'Var1_10'} = 'Eq10_P_kW';
%clear equip_data eq_processed_timetable eq_cell;

ON_OFF_double = table2array(eq_processed_table(:, 2:end));
ON_OFF_double(ON_OFF_double > 0) = 1;
ON_OFF_double(ON_OFF_double < 0) = 0;
ON_OFF_uint = uint8(ON_OFF_double);
clear ON_OFF_double;

figure,
for i = 1 : size(ON_OFF_uint, 2)
    subplot(numRows, numCols, i);
    plot(ON_OFF_uint(:, i));
end

column_names = string(eq_processed_table.Properties.VariableNames);
ON_OFF_table = array2table(ON_OFF_uint, 'VariableNames', column_names(2:end));
ON_OFF_table = addvars(ON_OFF_table, eq_processed_table.Time, 'Before', 1, 'NewVariableNames', 'Time');

clear  numCols numRows;



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
aggregate_table = table(eq_processed_table.Time, sum(eq_processed_table{:, 2:11}, 2), 'VariableNames', {'Time', 'P_kW'});
figure,
plot(aggregate_table.P_kW)

%% Split into training and validation data
trainingRatio = 0.8;
validationRatio = 1 - trainingRatio;

partition = cvpartition(size(eq_processed_table, 1), 'HoldOut', validationRatio);
trainingIndices = training(partition);
validationIndices = test(partition);

equipment_training = eq_processed_table(trainingIndices, :);
equipment_validation = eq_processed_table(validationIndices, :);

on_off_training = ON_OFF_table(trainingIndices, :);
on_off_validation = ON_OFF_table(validationIndices, :);

aggregate_training = aggregate_table(trainingIndices, :);
aggregate_validation = aggregate_table(validationIndices, :);


%% Save data

relativeFolderPath = '../../../data/processed/HIPE/1_week/';

writetable(equipment_training, fullfile(relativeFolderPath, 'equipment_training.csv'));
writetable(equipment_validation, fullfile(relativeFolderPath, 'equipment_validation.csv'));
writetable(on_off_training, fullfile(relativeFolderPath, 'on_off_training.csv'));
writetable(on_off_validation, fullfile(relativeFolderPath, 'on_off_validation.csv'));
writetable(aggregate_training, fullfile(relativeFolderPath, 'aggregate_training.csv'));
writetable(aggregate_validation, fullfile(relativeFolderPath, 'aggregate_validation.csv'));
