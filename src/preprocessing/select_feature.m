function [R_per_eq, R_per_unit, features_per_eq_sorted, features_unit_sorted] = select_feature(aggregate_power, features)
    % Objective: calculate the correlation coefficients
    % Input: each 'unit' for all equipment and aggregate power
    % Ouput: coefficient R(1, 2) for each equipment unit

    R_per_eq = zeros(1, size(features, 2));
    for i = 1:size(features, 2)
        R = corrcoef(aggregate_power, table2array(features(:, i)));
        R_per_eq(i) = R(1, 2);
    end

    R_per_unit = mean(reshape(R_per_eq, [6, ceil(size(R_per_eq, 2) / 6)]), 1);

    [~, R_per_eq_sorted_idx] = sort(abs(R_per_eq), 'descend');
    features_per_eq_sorted = (features.Properties.VariableNames(R_per_eq_sorted_idx));

    [~, R_per_unit_sorted_idx] = sort(abs(R_per_unit), 'descend');
    features_unit_sorted = features.Properties.VariableNames(R_per_unit_sorted_idx * 6);
    features_unit_sorted = regexprep(features_unit_sorted, '..$', '', 'lineanchors');
end