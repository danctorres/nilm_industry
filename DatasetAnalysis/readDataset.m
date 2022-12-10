%% Read dataset
% Daniel Torres
% 09/12/2022

% Dataset is in ./OriginalDataset
cd \\wsl.localhost\ubuntu\home\dtorres\Dissertation_NILM;
clear, close all, clc;

cd OriginalDataset/Equipment;
fileList = dir;
fileList = {fileList.name};
fileList=fileList(3:end);   % remove . and ..

n_Eq = size(fileList,2);
for i=1:n_Eq
    Eq_Data{i} = readtable(string(fileList(i)));
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
for i = 1 : size(Eq_Data,2)
    aux = Eq_Data{i};
    numbersSamples(i,:) = size(aux,1);
end

%% Not unique samples, Nan samples
numberSamples = [];
uniqueSamples = [];
notUniqueSamples = [];
nanSamplesCounter = zeros(1,8);
for i = 1 : size(Eq_Data,2)
    arrayEq = [];
    tableEq = Eq_Data{i};
    numberSamples(i) = size(tableEq,1);
    uniqueSamples(i) = size(unique(tableEq(:,1)),1);
    notUniqueSamples(i) = numberSamples(i) - size(unique(tableEq(:,1)),1);
    arrayEq = table2array(tableEq(:,2:end));
    for j = 1 : numberSamples(i)
        if ( (isnan(arrayEq(j,2)) + isnan(arrayEq(j,3)) + isnan(arrayEq(j,4)) + isnan(arrayEq(j,5))) > 0)
                nanSamplesCounter(i) = nanSamplesCounter(i) + 1;
        end
    end
end

% Starting and ending time samples
arrayStart = {};
arrayEnd = {};
for i = 1 : size(Eq_Data,2)
    tableEq = Eq_Data{i};
    arrayStart(i) = table2array(tableEq(1,1));
    arrayEnd(i) = table2array(tableEq(end,1));
end

