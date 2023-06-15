function [aggregate_corr] = calculate_corr(features_table)
    % Objective: calculate the correlation coefficients
    % Input: aggregates
    % Ouput: coefficient R(1, 2) for each aggregate unit

    aggregate_corr = zeros(1, size(features_table, 2) - 2);
    for i = 3:size(features_table, 2)
        R = corrcoef(table2array(features_table(:, 2)), table2array(features_table(:, i)));
        aggregate_corr(i - 2) = R(1, 2);
    end
end