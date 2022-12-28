%% Read dataset
% Daniel Torres
% 09/12/2022

% Dataset is in ./OriginalDataset
clear, close all, clc;
cd \\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\;

cd imdeld_dataset/Equipment;
file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end);   % remove . and ..

n_Eq = size(file_list,2);
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

for i = 1 : size(eq_data,2)
    aux = eq_data{i};
    number_samples(i,:) = size(aux,1);
end

%% Check number of Not unique samples and Nan samples
clearvars -except eq_data
number_samples = [];
unique_samples = [];
not_unique_samples = [];
nan_samples_counter = zeros(1,8);
for i = 1 : size(eq_data,2)
    table_eq = eq_data{i};
    number_samples(i) = size(table_eq,1);
    unique_samples(i) = size(unique(table_eq(:,1)),1);
    not_unique_samples(i) = number_samples(i) - size(unique(table_eq(:,1)),1);
    array_eq = [];
    array_eq = table2array(table_eq(:,2:end));
    for j = 1 : number_samples(i)
        if ( (isnan(array_eq(j,2)) + isnan(array_eq(j,3)) + isnan(array_eq(j,4)) + isnan(array_eq(j,5))) > 0)
                nan_samples_counter(i) = nan_samples_counter(i) + 1;
        end
    end
end

% Starting and ending time samples
array_start = {};
array_end = {};
for i = 1 : size(eq_data,2)
    tableEq = eq_data{i};
    array_start(i) = table2array(table_eq(1,1));
    array_end(i) = table2array(table_eq(end,1));
end


%% -> RUN THIS
% See common timestamps between 8 equipment
clearvars -except eq_data

% since the equipments may have duplicate samples, its needed to calculate
% the uniques from each equipment

all_dates = [];
for i = 1:size(eq_data, 2)
    table_eq = eq_data{i};
    dates = unique(table_eq.timestamp);
    datetime_values = cell2mat(dates);
    date_samples = datetime(datetime_values(:,1:end-3));
    all_dates = [all_dates; date_samples];
end

% AllC = {cat(1, eq_data{:})};
% dates = AllC{1}.timestamp;
[unique_values, ~, counts] = unique(all_dates);

unique_counts = unique(counts);
[N, edges] = histcounts(counts', [unique_counts', max(unique_counts)+1]);

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

common_timestamps = unique_values(N >= size(eq_data,2));
common_timestamps = sort(common_timestamps);


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

day1 = filtered_date_samples(find(diff_samples == max(diff_samples)))
day2 = filtered_date_samples(find(diff_samples == max(diff_samples))+1)

seconds(day2 - day1)

number_missing_samples = sum(diff_samples)
mean_missing_samples = mean(diff_samples)
median_missing_samples = median(diff_samples)


%% -> RUN THIS
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
    index = [index; find(idx == i)];
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


%% For each equipment, calculate the mean of not unique timestamps
clearvars -except eq_data days_common_timestamps

tableEq = eq_data{1};
mean_values = grpstats(tableEq, 'timestamp', 'mean', 'DataVars', 'active_power');

% Debug
% Check for duplicates
size(unique(mean_values.timestamp)) == size(mean_values.timestamp)

%% Spline interpolation
% Run previous block to calculate 
% Construct a table with the timestamps and active power values of the eight equipment
clearvars -except eq_data days_common_timestamps

time_power_array = table(days_common_timestamps, 'VariableNames', {'Date'});

for i = 1 : size(eq_data, 2)
    table_eq = eq_data{i};

    mean_values = grpstats(table_eq, 'timestamp', 'mean', 'DataVars', 'active_power');
        
%     dates_mat = cell2mat(table_eq.timestamp);
%     date_samples = datetime(datetime_values(:,1:end-3));
%     posix_date = posixtime(date_samples)
%     power = table_eq.active_power;
%     eq_array(:, 1) = posix_date
%     eq_array(:, 2) = power
%     mean_values = [unique(eq_array(:,1) ), accumarray(eq_array(:,1), eq_array(:,2), [], @mean)]

    datetime_values = cell2mat(mean_values.timestamp);
    dates_only = datetime(datetime_values(:,1:end-3));

    dates_only = unique (dates_only);

    [sharedvals,idx] = ismember(dates_only, days_common_timestamps);
    val = dates_only(sharedvals);
    index = find(idx ~= 0);

    % Debug
%     [sharedvals2,idx2] = ismember(days_common_timestamps, val);
%     val2 = days_common_timestamps(sharedvals2);
%     aux3 = find(idx2 == 0);
%     days_common_timestamps(aux3)
%     find(dates_only == days_common_timestamps(aux3))
%     datetime_values = cell2mat(common_timestamps);
%     date_samples = datetime(datetime_values(:,1:end-3));
%     find(date_samples == dates_only(aux3))
%     find (appended_categorical == categorical(days_common_timestamps(aux3)));

    active_power = mean_values.mean_active_power;
    active_power = active_power(index);
    
    name_collumn = sprintf('active_power_eq_%i', i);
    time_active_power_array.(name_collumn) = active_power;
end

% Debug
figure,
plot(time_active_power_array.active_power_eq_8)

%% Histogram samples equipment
clearvars -except eq_data

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

saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_equipment.fig');
saveas(gcf, '\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\imdeld_analysis\images\histogram_equipment.png');

