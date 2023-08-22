function [day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps)
% Objective: Calculate metrics for each equipment for the common_timestamps
% Input: equip_data, common_timestamps
% Output: diff_samples (array with difference between consecutive samples),
%         number_missing_samples (sum of all diff_samples, gives total of missing samples in common_timestamps),
%         mean_missing_samples (mean of the diff_samples)

    diff_samples = diff(posixtime(common_timestamps)) - 1;

    day1 = common_timestamps(diff_samples == max(diff_samples));
    day2 = common_timestamps(find(diff_samples == max(diff_samples)) + 1);
    interval = seconds(day2 - day1);

    number_missing_samples  = sum(diff_samples);
    mean_missing_samples    = mean(diff_samples);
    median_missing_samples  = median(diff_samples);
end