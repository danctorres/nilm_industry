% Objective: Read dataset
% Input: path_dataset (Optional - folder path of the nilm dataset equipment files)
% Output: equip_data (cell array, where each cell are each equipment samples)

function [equip_data] = read_equipment_csv(varargin)
    if (nargin == 1)
        cd(varargin{1});
    else
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        cd([erase(file_information.Filename, ['\imdeld_analysis\scripts\' file_name file_ext]) '\imdeld_dataset\Equipment']);
    end
    
    file_list = dir;
    file_list = {file_list.name};
    file_list = file_list(3:end); % remove . and ..
    
    n_Eq = size(file_list, 2);
    equip_data = cell(1, n_Eq);
    for i = 1:n_Eq
        equip_data{i} = readtable(string(file_list(i)));
    end

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    cd(erase(file_information.Filename, [file_name file_ext]));
end

% Comments:
% File names:
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