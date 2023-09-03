function [true_values_metrics, estimated_values_metrics] = calculate_metrics(true_values, estimated_values)
    true_values_metrics         = [];
    estimated_values_metrics    = [];
    true_max        = {};
    true_min        = {};
    true_mean       = {};
    true_median     = {};
    est_max         = {};
    est_min         = {};
    est_mean        = {};
    est_median      = {};

    for i = 1:size(true_values, 2)
        true_max{i}     = max(table2array(true_values{i}));
        true_min{i}     = min(table2array(true_values{i}));
        true_mean{i}    = mean(table2array(true_values{i}));
        true_median{i}  = median(table2array(true_values{i}));
        true_sum{i}     = sum(table2array(true_values{i}));
    end

    for i = 1:size(estimated_values, 2)
        est_max{i}      = max(table2array(estimated_values{i}));
        est_min{i}      = min(table2array(estimated_values{i}));
        est_mean{i}     = mean(table2array(estimated_values{i}));
        est_median{i}   = median(table2array(estimated_values{i}));
        est_sum{i}      = sum(table2array(estimated_values{i}));
    end

    true_values_metrics         = [true_max, true_min, true_mean, true_median, true_sum];
    estimated_values_metrics    = [est_max, est_min, est_mean, est_median, est_sum];
end
