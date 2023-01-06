% Objective: Calculate the average active power for each equipment equipment per day
% Input: equip_data, date_active_power
% Output: day_table_complete (table with the day and the active power for each equipment)

function [day_table_complete] = calculate_average_power_day(date_active_power)
    dates_only          = datetime(datestr(date_active_power.Date, 'dd-mmm-yyyy'));
    unique_dates        = unique(dates_only);
    [~, index_dates]    = ismember(dates_only, unique_dates);
    
    day_table_complete  = table(unique_dates(:), 'VariableNames', {'Date'});
    
    num_samples             = zeros(1, size(unique_dates, 1));
    mean_active_power       = zeros(1, size(unique_dates, 1));
    median_active_power     = zeros(1, size(unique_dates, 1));
    for j = 1:size(equip_data, 2)
        for i = 1:size(unique_dates, 1)
            num_samples(i)              = sum(index_dates == i);
            mean_active_power(i, j)     = round(mean(date_active_power{index_dates == i, j + 1}));
            median_active_power(i, j)   = round(median(date_active_power{index_dates == i, j + 1}));
        end
        day_table_complete.('Number_samples') = num_samples';
        day_table_complete.(sprintf('Mean_W_eq_%i', j)) = mean_active_power(:, j);
        day_table_complete.(sprintf('Median_W_eq_%i', j)) = median_active_power(:, j);
    end
end