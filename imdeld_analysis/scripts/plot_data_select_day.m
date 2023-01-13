function [] = plot_data_select_day(varargin)
    % Objective: Plot the active power values for all the equipment for one day
    % Input: equipment_formated.csv
    % Output: subplots_equipment_formated.fig, subplots_equipment_formated.png
    
    % varargin{1} -> path
    % varargin{2} -> true for saving figure into files
    
    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    
    if (nargin > 0)
        equipment_formated = varargin{1};
    else
        equipment_formated = readtable([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\equipment_formated.csv']);
    end
    
    dates_only = datetime(datestr(equipment_formated.timestamp, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only(varargin{2}));
    
    unit_label = string(varargin{3});
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(unique_dates, 1)
        sgtitle(string(unique_dates(i)))
        [sharedvals, ~] = (ismember(dates_only, unique_dates(i)));
        for j = 2:size(equipment_formated, 2)
            subplot((size(equipment_formated, 2) - 1) / 2, 2, j - 1)
            plot(table2array(equipment_formated(sharedvals, j)))
            title(sprintf('Equipment %i', j - 1))
            xlabel('Index')
            ylabel(unit_label)
        end
    end
    
    if (nargin > 0 && varargin{4} == true)
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_equipment_formated.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_equipment_formated.png']);
    end


end