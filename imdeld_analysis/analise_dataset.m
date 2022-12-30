%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% NILM dissertation dataset anaçysis code
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Daniel Torres
% 09/12/2022



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 1 - Read dataset -> RUN THIS 1st
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Dataset is in ./OriginalDataset

clear;  close all;  clc;
cd \\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\;

cd imdeld_dataset/Equipment;
file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end);   % remove . and ..

n_Eq = size(file_list,2);
eq_data = cell(1, n_Eq);
for i=1:n_Eq
    eq_data{i} = readtable(string(file_list(i)));
end

% 1 - 'doublepolecontactor-I.csv'	
% 2 - 'doublepolecontactor-II.csv'
% 3 - 'exhaustfan-I.csv'
% 4 - 'exhaustfan-II.csv'
% 5 - 'millingmachine-I.csv'
% 6 - 'millingmachine-II.csv'
% 7 - 'pelletizer-I.csv'
% 8 - 'pelletizer-II.csv'
% only care about data that include the 8 equipment

% columns of Eq_Data:
% 1 - timestamp
% 2 - active power
% 3 - reactive power
% 4 - apparent power
% 5 - current
% 6 - voltage


%% Check number of samples per equipment in the dataset
clearvars -except eq_data

number_samples = zeros(1, size(eq_data,2));
for i = 1 : size(eq_data,2)
    aux = eq_data{i};
    number_samples(i,:) = size(aux,1);
end

%% Check number of Not unique samples and Nan samples
clearvars -except eq_data
number_samples = zeros(1, size(eq_data,2));
unique_samples = zeros(1, size(eq_data,2));
not_unique_samples = zeros(1, size(eq_data,2));
nan_samples = zeros(1,8);   % incorrect size
nan_samples_counter = zeros(1,8);

for i = 1 : size(eq_data,2)
    table_eq = eq_data{i};
    number_samples(i) = size(table_eq,1);
    unique_samples(i) = size(unique(table_eq(:,1)),1);
    not_unique_samples(i) = number_samples(i) - size(unique(table_eq(:,1)),1);
    % array_eq = table2array(table_eq(:,2:end));
    aux_nan_counter = ones(size(table_eq,1), 1);
    nan_samples(i) = sum(aux_nan_counter(isnan(table_eq.active_power)));

    for j = 2 : 6
        nan_samples(i, j) = sum(aux_nan_counter(isnan(table_eq{:, j})));
    end
end

% Starting and ending time samples
array_start = cell(1, size(eq_data,2));
array_end = cell(1, size(eq_data,2));
for i = 1 : size(eq_data,2)
    table_eq = eq_data{i};
    array_start(i) = table2array(table_eq(1,1));
    array_end(i) = table2array(table_eq(end,1));
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 2 - Calculate the timestamp that equipment have in common -> RUN THIS 2nd
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% See common timestamps between 8 equipment
clearvars -except eq_data

% since the equipments may have duplicate samples, it is needed to calculate
% the uniques from each equipment

all_dates = [];
for i = 1:size(eq_data, 2)
    table_eq = eq_data{i};
    dates = unique(table_eq.timestamp);
    datetime_values = cell2mat(dates);
    date_samples = datetime(datetime_values(:,1:end-3));
    all_dates = cat(1, all_dates, date_samples);
    %all_dates = [all_dates; date_samples];
end

[unique_values, ~, counts] = unique(all_dates);

unique_counts = unique(counts);
[N, edges] = histcounts(counts', [unique_counts', max(unique_counts)+1]);

common_timestamps = unique_values(N >= size(eq_data,2));
common_timestamps = sort(common_timestamps);

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

% Alternative:
% appended_categorical = categorical(dates(1:end-3));
% 
% a = categories(appended_categorical);
% b = countcats(appended_categorical);
% common_timestamps = a(b == size(eq_data,2));
% 
% common_timestamps = sort(common_timestamps);
%edges = unique(AppendedCellTimestamps,'stable');
%b=cellfun(@(x) sum(ismember(AppendedCellTimestamps,x)),edges,'un',0);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Missing non consecutive timestamps
% Run previous code block to get the variable d
clearvars -except eq_data common_timestamps

posix_date = posixtime(common_timestamps);

% the minlength is the minimal size that a sequence of samples must have to
% be considered, this is, where a missing value can appear.
% minlength = 60;
% isconsecutive = diff(posix_date') == 1;
% seqedges = find(diff([false, isconsecutive, false]));
% seqstarts = seqedges(1:2:end);
% seqstops = seqedges(2:2:end);
% seqlengths = seqstops - seqstarts + 1;
% tokeep = seqlengths >=  minlength;
% indicestokeep = cell2mat(arrayfun(@(s, e) s:e, seqstarts(tokeep), seqstops(tokeep), 'UniformOutput', false));
% filtered_date_samples = date_samples(indicestokeep);
% filtered_posix = posix_date(indicestokeep);

% hours(seconds(size(date_samples, 1) - size(filtered_date_samples, 1)))

filtered_date_samples = common_timestamps;
filtered_posix = posix_date;

diff_samples = diff(filtered_posix) - 1;

day1 = filtered_date_samples(diff_samples == max(diff_samples));
day2 = filtered_date_samples(find(diff_samples == max(diff_samples))+1);

seconds(day2 - day1)

number_missing_samples = sum(diff_samples);
mean_missing_samples = mean(diff_samples);
median_missing_samples = median(diff_samples);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 3 - Calculate the timestamp that equipment have in common -> RUN THIS 3rd
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Find what are the days that are present and how many samples per day
clearvars -except eq_data common_timestamps

dates_only = datetime(datestr(common_timestamps, 'dd-mmm-yyyy'));

unique_dates = unique(dates_only);
counts = histcounts(dates_only', [unique_dates', max(unique_dates)+1]);

summary = table(unique_dates(:), counts(:), 'VariableNames', {'Date','count'});

% find days with more than 84600 samples
days_with_more_samples = summary(summary.count > 84600, :);

% get the common timestamps for the days_with_more_samples
[sharedvals,idx] = ismember(dates_only, days_with_more_samples.Date);

index = [];
for i = 1 : size(days_with_more_samples, 1)
    index = cat(1, index, find(idx == i));
end

days_common_timestamps = common_timestamps(index);

% Debug
% for i = 1 : size(days_with_more_samples.Date, 1)
%     aux = find(dates_only == days_with_more_samples.Date(i));
%     size_dates(i) = size(aux,1);
% end
% 
% sum(days_with_more_samples.count)
% size(days_common_timestamps)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% For each equipment, calculate the mean of not unique timestamps
clearvars -except eq_data days_common_timestamps

tableEq = eq_data{1};
mean_values = grpstats(tableEq, 'timestamp', 'mean', 'DataVars', 'active_power');

% Debug
% Check for duplicates
correct = size(unique(mean_values.timestamp)) == size(mean_values.timestamp);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 4 - Construct table dates and active power -> RUN THIS 4th
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Construct a table with the timestamps and active power values of the eight equipment
clearvars -except eq_data days_common_timestamps

date_active_power = table(days_common_timestamps, 'VariableNames', {'Date'});

for i = 1 : size(eq_data, 2)
    table_eq = eq_data{i};
    mean_values = grpstats(table_eq, 'timestamp', 'mean', 'DataVars', 'active_power');
    datetime_values = cell2mat(mean_values.timestamp);
    dates_only = datetime(datetime_values(:,1:end-3));
    dates_only = unique (dates_only);
    [sharedvals,idx] = ismember(dates_only, days_common_timestamps);
    val = dates_only(sharedvals);
    index = find(idx ~= 0);

    active_power = mean_values.mean_active_power;
    active_power = active_power(index);
    
    name_collumn = sprintf('active_power_eq_%i', i);
    date_active_power.(name_collumn) = active_power;

        % Debug
%     dates_mat = cell2mat(table_eq.timestamp);
%     date_samples = datetime(datetime_values(:,1:end-3));
%     posix_date = posixtime(date_samples)
%     power = table_eq.active_power;
%     eq_array(:, 1) = posix_date
%     eq_array(:, 2) = power
%     mean_values = [unique(eq_array(:,1) ), accumarray(eq_array(:,1), eq_array(:,2), [], @mean)]
%     [sharedvals2,idx2] = ismember(days_common_timestamps, val);
%     val2 = days_common_timestamps(sharedvals2);
%     aux3 = find(idx2 == 0);
%     days_common_timestamps(aux3)
%     find(dates_only == days_common_timestamps(aux3))
%     datetime_values = cell2mat(common_timestamps);
%     date_samples = datetime(datetime_values(:,1:end-3));
%     find(date_samples == dates_only(aux3))
%     find (appended_categorical == categorical(days_common_timestamps(aux3)));
end

% Debug
figure,
for i = 1 : size(eq_data, 2)
    subplot(size(eq_data, 2)/2, 2, i)
    plot(date_active_power{:, i+1})
    title (sprintf("Equipment %i", i));
    xlabel ("Sample")
    ylabel("Power [W]")
end

saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\dates_active_power.fig');
saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\dates_active_power.png');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% calculate average equipment active power per day
clearvars -except eq_data date_active_power

dates = date_active_power.Date;
%dates = time_active_power_array.timestamp;
dates_only = datetime(datestr(dates, 'dd-mmm-yyyy'));
unique_dates = unique(dates_only);
[~, index_dates] = ismember(dates_only, unique_dates);

day_table_complete = table(unique_dates(:), 'VariableNames', {'Date'});

num_samples = zeros(1, size(unique_dates, 1));
mean_active_power = zeros(1, size(unique_dates, 1));
median_active_power = zeros(1, size(unique_dates, 1));
for j = 1 : size(eq_data, 2)
    for i = 1 : size(unique_dates, 1)
        num_samples(i) = sum(index_dates == i);
        mean_active_power(i,j) = round(mean(date_active_power{index_dates == i, j + 1}));
        median_active_power(i,j) = round(median(date_active_power{index_dates == i, j + 1}));
    end
    mean_collumn = sprintf('Mean_W_eq_%i', j);
    median_collumn = sprintf('Median_W_eq_%i', j);

    day_table_complete.("Number_samples") = num_samples';
    day_table_complete.(mean_collumn) = mean_active_power(:,j);
    day_table_complete.(median_collumn) = median_active_power(:,j);
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 5 - Construct table dates and active power -> RUN THIS 5th
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Remove the 30-March-2018 from the days_common_timestamps and insert missing samples for each equipment
clearvars -except eq_data date_active_power dates dates_only

unique_dates = unique(dates_only);
% Remove the 30-Mar-2018 -> unique_dates(end - 1)
% filtered_dates_and_power = date_active_power(~ismember(dates_only, [unique_dates(end - 2), unique_dates(end - 1), unique_dates(end)]), :); 

filtered_dates_and_power = date_active_power(dates_only ~=  unique_dates(end - 1), :);

% Debug
% figure,
% for i = 1 : size(eq_data, 2)
%     subplot(size(eq_data, 2)/2, 2, i)
%     plot(filtered_dates_and_power{:, i+1})
%     title (sprintf("Equipment %i", i));
%     xlabel ("Sample")
%     ylabel("Power [W]")
% end

% Spline interpolation
% Define the data points
% date_dataset = posixtime(date_active_power.Date);
date_dataset = posixtime(filtered_dates_and_power.Date);

% Define the points used for interpolation
filtered_date_active_power = date_active_power(dates_only ~=  unique_dates(end - 1), :);
filtered_unique_dates = unique_dates(1:end - 2);
filtered_unique_dates = cat(1, filtered_unique_dates, unique_dates(end));

dates_complete = [];
for i = 1 : size(filtered_unique_dates, 1)
    date_year = year(filtered_unique_dates(i));
    date_month = month(filtered_unique_dates(i));
    date_day = day(filtered_unique_dates(i));
    seconds = 0:1:86400-1;  % all the seconds of the day
    dates_complete = cat (1, dates_complete, posixtime(datetime(date_year, date_month, date_day, 0, 0, seconds))');
end

diff = setdiff(dates_complete, date_dataset);           % points at which to interpolate
index_diff = find(ismember(dates_complete, diff));      % missing_indices
index_date_dataset = find(ismember(dates_complete, date_dataset));

active_power_complete = zeros(size(dates_complete, 1), size(eq_data, 2));
for i = 1 : size(eq_data, 2)
    y = filtered_date_active_power{:,i + 1};
    active_power_complete(index_date_dataset, i) = y;
    yi = spline(date_dataset, y, diff);  % Interpolate the data using a cubic spline
    % csaps / pchip
    active_power_complete(index_diff, i) = yi;
end


% Debug
% figure,
% for i = 1 : size(eq_data, 2)
%     subplot(size(eq_data, 2)/2, 2, i)
%     plot(active_power_complete(:, i))
%     title (sprintf("Equipment %i", i));
%     xlabel ("Sample")
%     ylabel("Power [W]")
% end

% size(dates_complete)
% size(active_power_complete)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% Histogram samples equipment
clearvars -except eq_data active_power_complete filtered_dates_and_power

% Original
figure
for i = 1 : size(eq_data,2)
    subplot(size(eq_data,2) / 2, 2, i);
    eq_table = eq_data{i};
    aux = table2array(eq_table(:,2));
    histogram(aux);
    title(sprintf("Equipment %i", i));
    xlabel('Power [W]')
    ylabel('Number of samples')
end

saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_original_equipment.fig');
saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_original_equipment.png');

% selected days
figure
for i = 1 : size(eq_data,2)
    subplot(size(eq_data,2) / 2, 2, i);
    histogram(active_power_complete(:, i));
    title(sprintf("Equipment %i", i));
    xlabel('Power [W]')
    ylabel('Number of samples')
end

saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_selected_days_equipment.fig');
saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_selected_days_equipment.png');


%% Read data from 'pelletizer-subcircuit.csv' (LVDB-2) and 'millingmachine-subcircuit.csv' (LVDB-3)
clearvars -except eq_data active_power_complete filtered_dates_and_power


cd \\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_dataset\;

LVDB2 = readtable('pelletizer-subcircuit.csv');
LVDB3 = readtable('millingmachine-subcircuit.csv');


%% Check linting
checkcode('analise_dataset.m')
