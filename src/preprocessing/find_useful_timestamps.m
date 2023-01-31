function [useful_common_timestamps] = find_useful_timestamps(common_timestamps)
    % Objective: Find the common timestamps that have more than 84600 samples
    % Input: equip_data, common_timestamps
    % Output: useful_common_timestamps (datetime arrray with the useful datetime samples from the dataset)


    dates_only = datetime(datestr(common_timestamps, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only);
    counts = histcounts(dates_only', [unique_dates', max(unique_dates) + 1]);
    % create table with the unique days, and number of samples
    summary = table(unique_dates(:), counts(:), 'VariableNames', {'Date', 'count'});
    
    % find days with more than 84600 samples
    threshold_number_samples = 83520;
    days_with_more_samples = summary(summary.count > threshold_number_samples, :);
    
    % get the common timestamps for the days_with_more_samples
    [~, idx] = ismember(dates_only, days_with_more_samples.Date);
    
    index = [];
    for i = 1:size(days_with_more_samples, 1)
        index = cat(1, index, find(idx == i));
    end
    
    useful_common_timestamps = common_timestamps(index);
    
    % Debug
    % for i = 1 : size(days_with_more_samples.Date, 1)
    %     aux = find(dates_only == days_with_more_samples.Date(i));
    %     size_dates(i) = size(aux,1);
    % end
    %
    % sum(days_with_more_samples.count)
    % size(useful_common_timestamps)
end

