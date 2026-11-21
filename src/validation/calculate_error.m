function metrics = calculate_error(true_vals, est_vals, convert_W_2_kW)
    % Objective: error metrics per column (machine), rows are samples, no rounding
    % Input: true_vals, est_vals (samples x machines), convert_W_2_kW (true when the values are in W)
    % Output: metrics (table, one row per column): MAE, MSE, RMSE (kW, kW^2, kW), R2, NDE, SAE (unitless)
    %   R2  = 1 - sum((est - true)^2) / sum((true - mean(true))^2)
    %   NDE = sum((est - true)^2) / sum(true^2)            normalised disaggregation error
    %   SAE = |sum(est) - sum(true)| / sum(true)           signal aggregate error

    if (convert_W_2_kW == true)
        true_vals = true_vals / 1000;
        est_vals = est_vals / 1000;
    end
    err     = est_vals - true_vals;
    MAE     = mean(abs(err))';
    MSE     = mean(err.^2)';
    RMSE    = sqrt(MSE);
    R2      = 1 - sum(err.^2)' ./ sum((true_vals - mean(true_vals)).^2)';
    NDE     = sum(err.^2)' ./ sum(true_vals.^2)';
    SAE     = abs(sum(est_vals) - sum(true_vals))' ./ sum(true_vals)';
    metrics = table(MAE, MSE, RMSE, R2, NDE, SAE);
end
