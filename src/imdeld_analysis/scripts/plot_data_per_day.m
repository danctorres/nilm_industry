function [] = plot_data_per_day(data, save)
    % Objective: Plot the formated data values for all the equipment per day
    % Input: data
    % Output: subplots_common_original.fig, subplots_common_original.png

    dates_only = datetime(datestr(data.Date, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only);
    
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(unique_dates, 1)
        legend_string = strings(1, size(data, 2) - 1);
        [sharedvals, ~] = ismember(dates_only, unique_dates(i));
        subplot((size(data, 2) - 1) / 2, 2, i)
        for j = 2:size(data, 2)
            plot(table2array(data(sharedvals, j)))
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
    
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_common_original.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\subplots_common_original.png']);
    end
end