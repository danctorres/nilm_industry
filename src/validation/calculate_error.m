function [MAE, MSE, RMSE, MAPE] = calculate_error(true_vals, est_vals, convert_W_2_kW)

    if (convert_W_2_kW == true)
        true_vals = true_vals / 1000;
        est_vals = est_vals / 1000;
    end
    MAE     = round(mean(abs(true_vals - est_vals)), 4);
    MSE     = round(mean((true_vals - est_vals).^2), 4);
    RMSE    = round(sqrt(MSE), 4);
    %MAPE    = round(mean(abs(true_vals - est_vals) ./ abs(true_vals) * 100), 4);
    %MaxAE   = max(abs(true_vals - est_vals));
end
