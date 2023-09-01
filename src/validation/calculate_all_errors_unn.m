function [error_hipe_states, error_hipe_fourier, error_imdeld_states, error_imdeld_fourier] = calculate_all_errors_unn(true_eq_hipe, est_hipe_states, est_hipe_fourier, true_eq_imdeld, est_imdeld_states, est_imdeld_fourier)
    MAE_hipe_states         = {};
    MSE_hipe_states         = {};
    RMSE_hipe_states        = {};
    
    MAE_hipe_fourier        = {};
    MSE_hipe_fourier        = {};
    RMSE_hipe_fourier       = {};
    
    MAE_imdeld_states       = {};
    MSE_imdeld_states       = {};
    RMSE_imdeld_states      = {};
    
    MAE_imdeld_fourier      = {};
    MSE_imdeld_fourier      = {};
    RMSE_imdeld_fourier     = {};
    
    for i = 1:size(true_eq_hipe, 2)
        true_vals   = table2array(true_eq_hipe{i});
    
        est_vals    = table2array(est_hipe_states{i});
        [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, false);
    
        MAE_hipe_states{end+1}      = MAE;
        MSE_hipe_states{end+1}      = MSE;
        RMSE_hipe_states{end+1}     = RMSE;
        
        est_vals    = table2array(est_hipe_fourier{i});
        [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, false);
    
        MAE_hipe_fourier{end+1}     = MAE;
        MSE_hipe_fourier{end+1}     = MSE;
        RMSE_hipe_fourier{end+1}    = RMSE;
    end
    
    true_vals   = table2array(true_eq_imdeld{1});
    
    est_vals    = table2array(est_imdeld_states{1});
    [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, true);
    
    MAE_imdeld_states{end+1}    = MAE;
    MSE_imdeld_states{end+1}    = MSE;
    RMSE_imdeld_states{end+1}   = RMSE;
    
    est_vals    = table2array(est_imdeld_fourier{1});
    
    [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, true);
    
    MAE_imdeld_fourier{end+1}   = MAE;
    MSE_imdeld_fourier{end+1}   = MSE;
    RMSE_imdeld_fourier{end+1}  = RMSE;
    
    error_hipe_states = {MAE_hipe_states, MSE_hipe_states, RMSE_hipe_states};
    error_hipe_fourier = {MAE_hipe_fourier, MSE_hipe_fourier, RMSE_hipe_fourier};
    error_imdeld_states = {MAE_imdeld_states, MSE_imdeld_states, RMSE_imdeld_states};
    error_imdeld_fourier = {MAE_imdeld_fourier, MSE_imdeld_fourier, RMSE_imdeld_fourier};
end
