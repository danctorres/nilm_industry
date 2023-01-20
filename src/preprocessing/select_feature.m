function [coeff, coeff_unit] = select_feature(aggregate_power, features)
    % Objective: calculate the correlation coefficients
    % Input: each 'unit' for all equipment and aggregate power
    % Ouput: coefficient R(1, 2) for each equipment unit

    coeff = zeros(1, size(features, 2));
    for i = 1:size(features, 2)
        R = corrcoef(aggregate_power, table2array(features(:, i)));
        coeff(i) = R(1, 2);
    end
    
    coeff_unit = mean(reshape(coeff, [6, ceil(size(coeff, 2) / 6)]), 1);
end