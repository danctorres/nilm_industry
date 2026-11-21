%% ------------------------------ VALIDATION ------------------------------ %%
% Compares the per-machine estimates in results/ with the ground truth in data/processed.
close all; clear; clc;

root    = fileparts(fileparts(fileparts(mfilename('fullpath'))));
hipe    = fullfile(root, 'data', 'processed', 'HIPE', '1_week');
imdeld  = fullfile(root, 'data', 'processed', 'IMDELD', 'data_6_equipment');
dl      = fullfile(root, 'results', 'deep_learning');
opt     = fullfile(root, 'results', 'optimization');


%% Read ground truth (timestamp, machine 1..M) and estimates (timestamp, measured aggregate, estimate 1..M)
true_hipe       = read_results_csv(fullfile(hipe, 'equipment_validation', 'eq_validation_*.csv'));
true_hipe_week  = read_results_csv(fullfile(hipe, 'undivided', 'equipment.csv'));
true_imdeld     = read_results_csv(fullfile(imdeld, 'equipment_validation.csv'));

est_emupf_hipe          = read_results_csv(fullfile(opt, 'HIPE', '1_week', 'estimated_active_power_*.csv'));
est_emupf_imdeld        = read_results_csv(fullfile(opt, 'IMDELD', 'estimated_active_power_*.csv'));
est_unn_hipe_states     = read_results_csv(fullfile(dl, 'HIPE', '1_week', 'states', 'estimated_active_power_*.csv'));
est_unn_hipe_fourier    = read_results_csv(fullfile(dl, 'HIPE', '1_week', 'fourier', 'estimated_active_power_*.csv'));
est_unn_imdeld_states   = read_results_csv(fullfile(dl, 'IMDELD', 'states', 'estimated_active_power_*.csv'));
est_unn_imdeld_fourier  = read_results_csv(fullfile(dl, 'IMDELD', 'fourier', 'estimated_active_power_*.csv'));

% Oracle-state baseline: hart_inspired.m reads the true on/off states of the whole HIPE week
est_oracle_hipe         = read_results_csv(fullfile(root, 'results', 'hart_inspired', 'HIPE', '1_week', 'estimations', 'estimations.csv'));
est_oracle_hipe{1}      = fillmissing(est_oracle_hipe{1}, 'constant', 0, 'DataVariables', @isnumeric);   % NaN = no estimate possible, scored as 0 kW


%% Errors per machine and of the reconstructed aggregate (sum of the estimates vs measured aggregate)
% label, ground truth, estimates, values in W (converted to kW)
runs = {
    'EMUPF HIPE',                       true_hipe,      est_emupf_hipe,         false
    'EMUPF IMDELD',                     true_imdeld,    est_emupf_imdeld,       true
    'UNN states HIPE',                  true_hipe,      est_unn_hipe_states,    false
    'UNN Fourier HIPE',                 true_hipe,      est_unn_hipe_fourier,   false
    'UNN states IMDELD',                true_imdeld,    est_unn_imdeld_states,  true
    'UNN Fourier IMDELD',               true_imdeld,    est_unn_imdeld_fourier, true
    'Oracle-state baseline HIPE',       true_hipe_week, est_oracle_hipe,        false
};

errors = cell(size(runs, 1), 2);
for r = 1:size(runs, 1)
    [errors{r, 1}, errors{r, 2}] = calculate_all_errors(runs{r, 2:4});
    fprintf('\n%s, per machine (MAE, RMSE in kW):\n', runs{r, 1});
    disp(errors{r, 1});
    fprintf('%s, aggregate reconstruction:\n', runs{r, 1});
    disp(errors{r, 2});
end


%% Max, min, mean, median and sum, and plots of true vs estimated power
stats = cell(size(runs, 1), 2);
for r = 1:size(runs, 1)
    truth_values    = cellfun(@(t) t(:, 2:end), runs{r, 2}, 'UniformOutput', false);
    est_values      = cellfun(@(t) t(:, 3:end), runs{r, 3}, 'UniformOutput', false);
    [stats{r, 1}, stats{r, 2}] = calculate_metrics(truth_values, est_values);

    unit = 'kW';
    if runs{r, 4}
        unit = 'W';
    end
    for j = 1:numel(truth_values)
        n = width(truth_values{j});
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
        sgtitle(sprintf('%s, %d machines', runs{r, 1}, n));
        for i = 1:n
            subplot(ceil(n / ceil(sqrt(n))), ceil(sqrt(n)), i)
            plot(truth_values{j}.(i), '.')
            hold on,
            plot(est_values{j}.(i), '.')
            hold off,
            title(strrep(truth_values{j}.Properties.VariableNames{i}, '_', ' '))
            xlabel('Sample Index', 'FontSize', 15);
            ylabel(sprintf('Active Power [%s]', unit), 'FontSize', 15);
            legend({'True'; 'Estimated'}, 'FontSize', 10);
        end
    end
end
