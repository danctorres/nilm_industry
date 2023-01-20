function [coeff] = select_feature(aggregate_power, features)
    % Objective: calculate the correlation coefficients
    % Input: each 'unit' for all equipment and aggregate power
    % Ouput: coefficient R(1, 2) for each equipment unit

    coeff = zeros(1, size(features, 2));
    for i = 1:size(features, 2)
        x = table2array(features);
        R = corrcoef(x(:, i), table2array(aggregate_power));
        coeff(i) = R(1, 2);
    end
end