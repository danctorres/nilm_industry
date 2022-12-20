%% Read dataset
% Daniel Torres
% 09/12/2022

% Dataset is in ./OriginalDataset
cd \\wsl.localhost\ubuntu\home\dtorres\Dissertation_NILM;
clear, close all, clc;

cd OriginalDataset/Equipment;
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


%% Total number of samples
clearvars -except eq_data
for i = 1 : size(eq_data,2)
    aux = eq_data{i};
    numbers_samples(i,:) = size(aux,1);
end

%% Not unique samples, Nan samples
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

appended_tst = [];
for i = 1 : size(eq_data,2)
    table_eq = eq_data{i};
    appended_tst = [appended_tst; categorical((table_eq(:,1).timestamp))];
end

a = categories(appended_tst);
b = countcats(appended_tst);
d = a(b == size(eq_data,2));

%edges = unique(AppendedCellTimestamps,'stable');
%b=cellfun(@(x) sum(ismember(AppendedCellTimestamps,x)),edges,'un',0);

%% Missing non consecutive timestamps
% Run previous code block
clearvars -except eq_data

aux = cell2mat(d);
date_samples = datetime(aux(:,1:end-3));
posix_date = posixtime(date_samples);
observations = find(diff(posix_date) ~= 1) + 1;

aux_date = d;
aux_date(observations) = [];

observations_datetime = find(diff(dateSamples) ~= seconds(1)) + seconds(1);
% date = today("datetime")


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