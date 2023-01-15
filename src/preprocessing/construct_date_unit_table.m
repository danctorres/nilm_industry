function [date_unit] = construct_date_unit_table(equip_data, useful_common_timestamps, unit)
    % Objective: Construct a table with the timestamps and active power values of the eight equipment
    % Input: equip_data, useful_common_timestamps
    % Output: date_active_power (table with timestamp and active power values for eight equipment)

    date_unit = table(useful_common_timestamps, 'VariableNames', {'Date'});
    for i = 1:size(equip_data, 2)
        mean_values         = grpstats(equip_data{i}, 'timestamp', 'mean', 'DataVars', string(unit));
        datetime_values     = cell2mat(mean_values.timestamp);
        [sharedvals, ~]     = ismember(unique(datetime(datetime_values(:, 1:end - 3))), useful_common_timestamps);
    
        date_unit.(join([ string(unit) sprintf('%i', i)], '_')) = table2array(mean_values(sharedvals, 3));
    end
end