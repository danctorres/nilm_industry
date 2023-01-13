function [date_active_power] = construct_date_unit_table(equip_data, useful_common_timestamps)
    % Objective: Construct a table with the timestamps and active power values of the eight equipment
    % Input: equip_data, useful_common_timestamps
    % Output: date_active_power (table with timestamp and active power values for eight equipment)

    date_active_power = table(useful_common_timestamps, 'VariableNames', {'Date'});
    for i = 1:size(equip_data, 2)
        table_eq            = equip_data{i};
        mean_values         = grpstats(table_eq, 'timestamp', 'mean', 'DataVars', 'active_power');
        datetime_values     = cell2mat(mean_values.timestamp);
        dates_only          = unique(datetime(datetime_values(:, 1:end - 3)));
        [sharedvals, ~]     = ismember(dates_only, useful_common_timestamps);
    
        active_power = mean_values.mean_active_power(sharedvals);
        date_active_power.(sprintf('active_power_eq_%i', i)) = active_power;
    end
end