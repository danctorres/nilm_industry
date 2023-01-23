function [aggregate_corr] = calculate_corr(aggregate)
    % Objective: calculate the correlation coefficients
    % Input: aggregates
    % Ouput: coefficient R(1, 2) for each aggregate unit

    aggregate_corr = zeros(1, size(aggregate, 2) - 2);
    for i = 3:size(aggregate, 2)
        R = corrcoef(table2array(aggregate(:, 2)), table2array(aggregate(:, i)));
        aggregate_corr(i - 2) = R(1, 2);
    end
end