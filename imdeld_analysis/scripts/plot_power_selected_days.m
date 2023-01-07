% Objective: Plot the active power values for all the equipment per day
% Input: equipment_formated.csv
% Output: subplots_equipment_formated.fig, subplots_equipment_formated.png

function [] = plot_power_selected_days(varargin)
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
    unique_dates = unique(dates_only);
    
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(unique_dates, 1)
        legend_string = strings(1, size(equipment_formated, 2) - 1);
        [sharedvals, ~] = (ismember(dates_only, unique_dates(i)));
        subplot((size(equipment_formated, 2) - 1) / 2, 2, i)
        for j = 2:size(equipment_formated, 2)
            plot(table2array(equipment_formated(sharedvals, j)))
            hold on;
            legend_string(j - 1) = string(sprintf('Eq. %i', j - 1));
        end
        lgd = legend(legend_string);
        lgd.FontSize = 7;
        lgd.NumColumns = 2;
        title(string(unique_dates(i)))
        xlabel('Index')
        ylabel('Active Power [W]')
        hold off;
    end
    
    if (nargin > 0 && varargin{2} == true)
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_equipment_formated.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_equipment_formated.png']);
    end

end