function [error_hipe, error_imdeld] = calculate_all_errors_emupf(true_eq_hipe, est_hipe, true_eq_imdeld, est_imdeld)
    MAE_hipe    = {};
    MSE_hipe    = {};
    RMSE_hipe   = {};
    MAPE_hipe   = {};

    MAE_imdeld  = {};
    MSE_imdeld  = {};
    RMSE_imdeld = {};

    for i = 1:size(true_eq_hipe, 2)
        true_vals   = table2array(true_eq_hipe{i});
    
        est_vals    = table2array(est_hipe{i});
        [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, false);
    
        MAE_hipe{end+1}      = MAE;
        MSE_hipe{end+1}      = MSE;
        RMSE_hipe{end+1}     = RMSE;
       
    end
    
    true_vals   = table2array(true_eq_imdeld);
    
    est_vals    = table2array(est_imdeld{1});
    [MAE, MSE, RMSE] = calculate_error(true_vals, est_vals, true);
    
    MAE_imdeld{end+1}    = MAE;
    MSE_imdeld{end+1}    = MSE;
    RMSE_imdeld{end+1}   = RMSE;
    
    error_hipe = {MAE_hipe, MSE_hipe, RMSE_hipe};
    error_imdeld = {MAE_imdeld, MSE_imdeld, RMSE_imdeld};
end
