function [date_unit] = construct_date_unit_table(equip_data, useful_common_timestamps, unit, selected_eq)
    % Objective: Construct a table with the timestamps and data values of the selected equipment
    % Input: equip_data, useful_common_timestamps
    % Output: date_unit (table with timestamp and data values for the selected equipment)

    date_unit = table(useful_common_timestamps, 'VariableNames', {'Date'});
    for i = 1:size(selected_eq, 2)
        mean_values         = grpstats(equip_data{selected_eq(i)}, 'timestamp', 'mean', 'DataVars', string(unit));
        datetime_values     = cell2mat(mean_values.timestamp);
        [sharedvals, ~]     = ismember(unique(datetime(datetime_values(:, 1:end - 3))), useful_common_timestamps);
    
        date_unit.(join([ string(unit), string(selected_eq(i))], '_')) = table2array(mean_values(sharedvals, 3));
    end
end