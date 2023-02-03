function [useful_common_timestamps] = find_useful_timestamps(common_timestamps)
    % Objective: Find the common timestamps that have more than 84600 samples
    % Input: equip_data, common_timestamps
    % Output: useful_common_timestamps (datetime arrray with the useful datetime samples from the dataset)


    dates_only = datetime(datestr(common_timestamps, 'dd-mmm-yyyy'));
    [unique_dates, ~, indices] = unique(dates_only);

    % Calculate max difference between samples
    start_indices = [1; find(diff(indices)) + 1];
    end_indices = [find(diff(indices)); size(dates_only, 1)];
    max_diff = zeros(size(unique_dates, 1), 1);
    for i = 1:size(unique_dates, 1)
        max_diff(i, 1) = seconds(max(diff(common_timestamps(start_indices(i):end_indices(i)))));
    end

    counts = histcounts(dates_only', [unique_dates', max(unique_dates) + 1]);

    % create table with the unique days, and number of samples
    summary = table(unique_dates(:), counts(:), max_diff(:), 'VariableNames', {'date', 'count', 'max_diff'});
    
    % find days with more than 84600 samples 83520
    threshold_total_missing = 2880;
    threshold_interval = 15;
    days_with_more_samples = summary(summary.count > (86400 - threshold_total_missing) & (summary.max_diff < threshold_interval), :);
    
    % get the common timestamps for the days_with_more_samples
    [~, idx] = ismember(dates_only, days_with_more_samples.date);
    
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

