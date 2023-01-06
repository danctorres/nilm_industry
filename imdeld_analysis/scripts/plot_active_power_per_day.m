% Objective: Plot the active power values for all the equipment per day 
% Input: date_active_power
% Output: subplots_common_original.fig, subplots_common_original.png

function [] = plot_active_power_per_day(date_active_power, varargin)
    dates_only = datetime(datestr(date_active_power.Date, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only);
    
    figure('units','normalized','outerposition',[0 0 1 1])
    for i = 1:size(unique_dates, 1)
        legend_string = strings(1, size(date_active_power, 2) - 1);
        [sharedvals, ~] = ismember(dates_only, unique_dates(i));
        subplot((size(date_active_power, 2) - 1) / 2, 2, i)
        for j = 2:size(date_active_power, 2)
            plot(table2array(date_active_power(sharedvals, j)))
            hold on;
            legend_string(j - 1) = string(sprintf('Eq. %i', j - 1));
        end
        lgd = legend(legend_string);
        lgd.FontSize = 7;
        lgd.NumColumns = 2;
        title(string(unique_dates(i)))
        xlabel('Second [s]')
        ylabel('Active Power [W]')
        hold off;
    end
    
    if (nargin == 1 && varargin{1} == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\' file_name file_ext]) '\results\images\subplots_common_original.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\' file_name file_ext]) '\results\images\subplots_common_original.png']);
    end
end