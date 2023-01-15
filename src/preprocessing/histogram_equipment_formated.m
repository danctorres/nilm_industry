function [] = histogram_equipment_formated(equipment_formated, varargin)
    % Objective: Create histograms of all the equipment active power samples for selected days
    % Input: equipment_formated
    % Output: histogram images

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(equipment_formated, 2) - 1
        subplot((size(equipment_formated, 2) - 1) / 2, 2, i)
        histogram( table2array(equipment_formated(:, i + 1)));
        title(sprintf('Equipment %i', i))
        xlabel('Power [W]')
        ylabel('Number of samples')
    end
    
    if (nargin == 1 && varargin{1} == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_formated.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_formated.png']);
    end
end