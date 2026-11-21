%% ------------------ HART-INSPIRED ORACLE-STATE BASELINE ------------------ %%
% Estimates each machine's power from the step in the aggregate at its OFF event.
% It reads the TRUE on/off states, so it is an oracle-state reference, not an unsupervised NILM method.
close all; clear; clc;

%% Read the undivided HIPE week
root        = fileparts(fileparts(fileparts(mfilename('fullpath'))));
undivided   = fullfile(root, 'data', 'processed', 'HIPE', '1_week', 'undivided');
agg_table   = readtable(fullfile(undivided, 'aggregate.csv'));
st_table    = readtable(fullfile(undivided, 'states.csv'));
eq_table    = readtable(fullfile(undivided, 'equipment.csv'));


%% Get equipment values at events
change_indices_table = {};

ALL_EVENTS_AGG_IDX = [];
ALL_EVENTS_STATE_CHANGE = [];
ALL_EVENTS_EQ_ID = [];
for i = 2:size(st_table, 2)
    diff_arr = diff(table2array(st_table(:, i)));
    change_indices = find(diff_arr ~= 0) + 1;
    change_indices_table{i - 1} = change_indices;

    diff_arr(diff_arr == 0) = [];

    ALL_EVENTS_AGG_IDX = [ALL_EVENTS_AGG_IDX; change_indices_table{i - 1}];
    ALL_EVENTS_EQ_ID = [ALL_EVENTS_EQ_ID; ((i - 1) * ones(size(diff_arr, 1), 1) )];
    ALL_EVENTS_STATE_CHANGE = [ALL_EVENTS_STATE_CHANGE; diff_arr];
end

[ALL_EVENTS_AGG_IDX, sorting_idx] = sort(ALL_EVENTS_AGG_IDX);
ALL_EVENTS_EQ_ID = ALL_EVENTS_EQ_ID(sorting_idx);
ALL_EVENTS_STATE_CHANGE = ALL_EVENTS_STATE_CHANGE(sorting_idx);

clear diff_arr change_indices sorting_idx i;


%% Estimation
est_2_samples_OFF_event = estimation_using_2_samples_OFF_event(table2array(st_table(:, 2:end)), agg_table.P_kW, ALL_EVENTS_AGG_IDX, ALL_EVENTS_EQ_ID, ALL_EVENTS_STATE_CHANGE);

figure,
for i = 1:size(est_2_samples_OFF_event, 2)
    subplot(round(size(est_2_samples_OFF_event, 2) / 2), 2, i)
    plot(eq_table{:, i + 1})
    hold on
    plot(est_2_samples_OFF_event(:, i), '.')
end


%% Save estimations: Time, aggregate, one estimate per machine (same column layout as the other methods' results)
variables_names = strrep(st_table.Properties.VariableNames(2:end), '_State', '_P_kW');
estimations_table = [agg_table, array2table(est_2_samples_OFF_event, 'VariableNames', variables_names)];
writetable(estimations_table, fullfile(root, 'results', 'hart_inspired', 'HIPE', '1_week', 'estimations', 'estimations.csv'));


%% Plot
figure,
for i = 1:size(st_table, 2) - 1
    subplot(3, 1, 1)
    plot(i * table2array(st_table(:, i + 1)))
    hold on
end
subplot(3, 1, 2)
plot(sum(table2array(st_table(:, 2:end)), 2))
subplot(3, 1, 3)
plot(diff(sum(table2array(st_table(:, 2:end)), 2)))
