% Objective: Find common timestamps between 8 equipment
% Input: equip_data (cell array with equipment samples)
% Output: common_timestamps (datetime sorted arrray with the dates of the common timestamp between the equipment)

function [common_timestamps] = find_common_timestamps(equip_data)
    all_dates = [];
    for i = 1:size(equip_data, 2)
        table_eq = equip_data{i};
        datetime_values = cell2mat(unique(table_eq.timestamp));
        all_dates = cat(1, all_dates, datetime(datetime_values(:, 1:end-3)));
    end

    % equipments may have duplicate samples, find unique from each equipment
    [unique_values, ~, counts] = unique(all_dates);
    
    unique_counts = unique(counts);
    [N, ~] = histcounts(counts', [unique_counts', max(unique_counts) + 1]);
    
    common_timestamps = sort(unique_values(N >= size(equip_data, 2)));
end

% Debug
% max(N) =  2536039     2536040     2536041     2536042     2536043     2536044     2536045     2536046     2536047
% datetime_values = cell2mat(dates);
% date_samples = datetime(datetime_values(:,1:end-3));
%
% aux = (unique_values(2536039));
% aux2 = cell2mat(aux);
% aux2 = datetime(aux2(:,1:end-3));
% aux3 = find(date_samples == aux2);
% size(aux3, 1) == max(N)
