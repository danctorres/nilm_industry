function [common_timestamps] = find_common_timestamps(equip_data, eq_index)
    % Objective: Find common timestamps between 8 equipment
    % Input: equip_data (cell array with equipment samples), eq_index (array with the index of the equipment to consider)
    % Output: common_timestamps (datetime sorted arrray with the dates of the common timestamp between the equipment)

    all_dates = [];
    for i = 1:size(eq_index, 2)
        datetime_values = cell2mat(unique(equip_data{eq_index(i)}.timestamp));
        all_dates = cat(1, all_dates, datetime(datetime_values(:, 1:end - 3)));
    end
    
    [unique_values, ~, counts]  = unique(all_dates);
    unique_counts               = unique(counts);
    [N, ~]                      = histcounts(counts', [unique_counts', max(unique_counts) + 1]);
    common_timestamps           = sort(unique_values(N >= size(eq_index, 2)));
end
