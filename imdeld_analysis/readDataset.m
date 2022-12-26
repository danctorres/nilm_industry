%% Read dataset
% Daniel Torres
% 09/12/2022

% Dataset is in ./OriginalDataset
cd \\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\;
clear, close all, clc;

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

%% See commun timestamps between 8 equipment
clearvars -except eq_data
table_eq = eq_data{1};

AllC = {cat(1, eq_data{:})};
appended_categorical = categorical(AllC{1}.timestamp);
appended_categorical = sort(appended_categorical);

a = categories(appended_categorical);
b = countcats(appended_categorical);
commun_timestamps = a(b == size(eq_data,2));

%edges = unique(AppendedCellTimestamps,'stable');
%b=cellfun(@(x) sum(ismember(AppendedCellTimestamps,x)),edges,'un',0);

%% Missing non consecutive timestamps
% Run previous code block to get the variable d
clearvars -except eq_data commun_timestamps

aux = cell2mat(commun_timestamps);
date_samples = datetime(aux(:,1:end-3));
posix_date = posixtime(date_samples);
%observations = find(diff(posix_date) ~= 1) + 1; 


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

filtered_date_samples = date_samples;
filtered_posix = posix_date;


diff_samples = diff(filtered_posix) - 1;

day1 = filtered_date_samples(find(diff_samples == max(diff_samples)))
day2 = filtered_date_samples(find(diff_samples == max(diff_samples))+1)

seconds(day2 - day1)

number_missing_samples = sum(diff_samples)
mean_missing_samples = mean(diff_samples)
median_missing_samples = median(diff_samples)


%%
clearvars -except Eq_Data

nanSamplesCounter = zeros(1,8);
for i = 1 : size(Eq_Data,2)
    tableEq = Eq_Data{i};
    arrayEq = [];
    
    arrayEq = cell2mat(table2array(tableEq(:,1)));
    arrayEq = arrayEq(j, 1:end-3);
    for j = 1 : size(arrayEq,1)
        timeEq(j,:) = convertCharsToStrings(arrayEq(j,:));
    end

    A() = convertCharsToStrings(arrayEq(j, 1:end-3));
    A = cellfun(@calculateDatetime,arrayEq);
end

function datetimeX = calculateDatetime(x)
    datetimeX = (convertCharsToStrings(x(1:end-3)));
end