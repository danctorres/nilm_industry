function [MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals)
    MAE     = round(mean(abs(true_vals - est_vals)), 4);
    MSE     = round(mean((true_vals - est_vals).^2), 4);
    RMSE    = round(sqrt(MSE), 4);
    MAPE    = round(mean(abs(true_vals - est_vals)), 4);
    %MaxAE   = max(abs(true_vals - est_vals));
end