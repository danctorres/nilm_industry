close all; clear; clc;

%% Read training data
file_information = matlab.desktop.editor.getActive;
[file_path, ~, ~] = fileparts(file_information.Filename);
file_path_agg = [erase(file_path, 'src\hart_inspired'), 'data\processed\HIPE\1_week\undivided\aggregate.csv'];
file_path_st = [erase(file_path, 'src\hart_inspired'), 'data\processed\HIPE\1_week\undivided\states.csv'];
file_path_eq = [erase(file_path, 'src\hart_inspired'), 'data\processed\HIPE\1_week\undivided\equipment.csv'];

agg_table = readtable(file_path_agg);
st_table = readtable(file_path_st);
eq_table = readtable(file_path_eq);

file_information = matlab.desktop.editor.getActive;
[file_path, ~, ~] = fileparts(file_information.Filename);
cd (file_path)

clear file_information file_path file_path_agg file_path_st file_path_eq;


%% Get equipment values at events
% signatures = {};
change_indices_table = {};
for i = 2:size(st_table, 2)
    diff_arr = diff(table2array(st_table(:, i)));
    change_indices = find(diff_arr ~= 0);
%     signatures{i - 1} = abs(table2array(agg_table(change_indices + 1, 2)) - table2array(agg_table(change_indices, 2)));
    change_indices_table{i - 1} = change_indices;
end

clear diff_arr change_indices i;


%% Save signatures

% relativeFolderPath = '../../results/hart_inspired/HIPE/1_week/signatures/';
% for i = 1:size(signatures, 2)
%     writetable(array2table(unique(round(signatures{i}, 4)), 'VariableNames', {'P_kW'}), fullfile([relativeFolderPath], sprintf('eq_%d.csv', i)));
% end


%% Plot
figure,
for i = 1:size(st_table, 2) - 2
    subplot(3, 1, 1)
    plot(i * table2array(st_table(:, i + 1)))
    hold on
end
subplot(3, 1, 2)
plot(sum(table2array(st_table(:, 2:8)), 2))
subplot(3, 1, 3)
plot(diff(sum(table2array(st_table(:, 2:8)), 2)))

for i = 1:size(st_table, 2) - 2
    subplot(3, 1, 1)
    plot(i * table2array(st_table(:, i + 1)))
    hold on
end


%% Estimation

agg = agg_table.P_kW;

estimations = estimation(st_table, change_indices_table, agg);



