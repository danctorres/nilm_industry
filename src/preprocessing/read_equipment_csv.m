function [equip_data] = read_equipment_csv(folder)
    % Objective: Read every machine csv file in folder
    % Input: folder (path of the dataset Equipment folder)
    % Output: equip_data (cell array, one table per machine, in alphabetical file order)

    file_list = dir(fullfile(folder, '*.csv'));
    equip_data = cell(1, numel(file_list));
    for i = 1:numel(file_list)
        equip_data{i} = readtable(fullfile(folder, file_list(i).name));
    end
end

% Comments:
% IMDELD file names:
% 1 - 'doublepolecontactor-I.csv'
% 2 - 'doublepolecontactor-II.csv'
% 3 - 'exhaustfan-I.csv'
% 4 - 'exhaustfan-II.csv'
% 5 - 'millingmachine-I.csv'
% 6 - 'millingmachine-II.csv'
% 7 - 'pelletizer-I.csv'
% 8 - 'pelletizer-II.csv'
% columns of equip_data:
% 1 - timestamp
% 2 - active power
% 3 - reactive power
% 4 - apparent power
% 5 - current
% 6 - voltage
