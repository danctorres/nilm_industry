close all; clear; clc;

%% Read data
% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd(file_dir)

%% estimation UNN HIPE and IMDELD
estimations_unn_dir_hipe    = [erase(file_dir,'src\validation'), 'results\deep_learning\HIPE\1_week'];
est_unn_hipe_states         = read_results_csv(dir(join([estimations_unn_dir_hipe, '\states'])));
est_unn_hipe_fourier        = read_results_csv(dir(join([estimations_unn_dir_hipe, '\fourier'])));

estimations_unn_dir_imdeld  = [erase(file_dir,'src\validation'), 'results\deep_learning\IMDELD'];
est_unn_imdeld_states       = read_results_csv(dir(join([estimations_unn_dir_imdeld, '\states'])));
est_unn_imdeld_fourier      = read_results_csv(dir(join([estimations_unn_dir_imdeld, '\fourier'])));

true_dir_hipe               = [erase(file_dir,'src\validation'), 'data\processed\HIPE\1_week'];
true_eq_hipe                = read_results_csv(dir(join([true_dir_hipe, '\equipment_validation'])));

true_dir_imdeld             = [erase(file_dir,'src\validation'), 'data\processed\IMDELD\data_6_equipment'];
true_eq_imdeld              = readtable(join ([true_dir_imdeld, '\equipment_validation.csv']));

est_values_hipe_mat     = [];
true_values_hipe_mat    = [];
MAE_hipe_states         = {};
MSE_hipe_states         = {};
RMSE_hipe_states        = {};
MAPE_hipe_states        = {};

MAE_hipe_fourier        = {};
MSE_hipe_fourier        = {};
RMSE_hipe_fourier       = {};
MAPE_hipe_fourier       = {};

MAE_imdeld_states       = {};
MSE_imdeld_states       = {};
RMSE_imdeld_states      = {};
MAPE_imdeld_states      = {};

MAE_imdeld_fourier      = {};
MSE_imdeld_fourier      = {};
RMSE_imdeld_fourier     = {};
MAPE_imdeld_fourier     = {};

for i = 1:size(true_eq_hipe, 2)
    true_table  = true_eq_hipe{i};
    true_vals   = table2array(true_table(:, end-i:end));

    est_table   = est_unn_hipe_states{i};
    est_vals    = table2array(est_table(:, end-i:end));
    [MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals);

    MAE_hipe_states{end+1}      = MAE;
    MSE_hipe_states{end+1}      = MSE;
    RMSE_hipe_states{end+1}     = RMSE;
    MAPE_hipe_states{end+1}     = MAPE;
    
    est_table   = est_unn_hipe_fourier{i};
    est_vals    = table2array(est_table(:, end-i:end));
    [MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals);

    MAE_hipe_fourier{end+1}     = MAE;
    MSE_hipe_fourier{end+1}     = MSE;
    RMSE_hipe_fourier{end+1}    = RMSE;
    MAPE_hipe_fourier{end+1}    = MAPE;
end

true_table  = true_eq_imdeld;
true_vals   = table2array(true_table(:, 2:end));

est_table   = est_unn_imdeld_states{1};
est_vals    = table2array(est_table(:, 3:end));
[MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals);

MAE_imdeld_states{end+1}    = MAE;
MSE_imdeld_states{end+1}    = MSE;
RMSE_imdeld_states{end+1}   = RMSE;
MAPE_imdeld_states{end+1}   = MAPE;

est_table   = est_unn_imdeld_fourier{1};
est_vals    = table2array(est_table(:, 3:end));

[MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals);

MAE_imdeld_fourier{end+1}   = MAE;
MSE_imdeld_fourier{end+1}   = MSE;
RMSE_imdeld_fourier{end+1}  = RMSE;
MAPE_imdeld_fourier{end+1}  = MAPE;

