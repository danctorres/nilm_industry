%% Read dataset
% Daniel Torres
% 09/12/2022

% Dataset is in ./OriginalDataset

cd OriginalDataset/Equipment;
fileList = dir;
fileList = {fileList.name};
fileList=fileList(3:end);   % remove . and ..

n_Eq = size(fileList,2);
Eq_Data = cell{n_Eq};
for i=1:n_Eq
    Eq_Data{i} = readmatrix(string(fileList(i)));
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
