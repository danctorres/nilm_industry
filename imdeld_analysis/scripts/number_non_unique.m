% Objective: Check number of Not unique samples and Nan samples
% Input: equip_data
% Output: number_samples (array with the number of timesamples that each equipment has)

function [number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data)
    number_samples      = zeros(1, size(equip_data, 2));
    unique_samples      = zeros(1, size(equip_data, 2));
    not_unique_samples  = zeros(1, size(equip_data, 2));
    nan_samples         = zeros(1, size(equip_data, 2)); % initialized with incorrect size
    
    for i = 1:size(equip_data, 2)
        table_eq                = equip_data{i};
        number_samples(i)       = size(table_eq, 1);
        unique_samples(i)       = size(unique(table_eq(:, 1)), 1);
        not_unique_samples(i)   = number_samples(i) - size(unique(table_eq(:, 1)), 1);
        nan_samples_counter     = ones(size(table_eq, 1), 1);
        nan_samples(i)          = sum(nan_samples_counter(isnan(table_eq.active_power)));
    
        for j = 2:6
            nan_samples(i, j) = sum(nan_samples_counter(isnan(table_eq{:, j})));
        end
    end
    
    % Starting and ending time samples
    array_start = cell(1, size(equip_data, 2));
    array_end   = cell(1, size(equip_data, 2));
    for i = 1:size(equip_data, 2)
        table_eq        = equip_data{i};
        array_start(i)  = table2array(table_eq(1, 1));
        array_end(i)    = table2array(table_eq(end, 1));
    end
end