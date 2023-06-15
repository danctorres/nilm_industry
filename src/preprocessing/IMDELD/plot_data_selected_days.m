function [] = plot_data_selected_days(data, units, save)
    % Objective: Plot the data values for all the equipment per day
    % Input: equipment_formated.csv
    % Output: subplots_equipment_formated.fig, subplots_equipment_formated.png
    

    
    %if (nargin == 3)
    %    data = varargin{1};
    % else
    %    data = readtable([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), ['\data\interim\IMDELD\', string(varargin{2}), '.csv']]);
    % end
    
    dates_only = datetime(datestr(data.timestamp, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only);
    
    unit_label = string(units);
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(unique_dates, 1)
        legend_string = strings(1, size(data, 2) - 1);
        [sharedvals, ~] = (ismember(dates_only, unique_dates(i)));
        subplot(round(size(unique_dates, 1) / 2), 2, i)
        for j = 2:size(data, 2)
            plot(table2array(data(sharedvals, j)))
            hold on;
            legend_string(j - 1) = string(sprintf('Eq. %i', j - 1));
        end
        lgd = legend(legend_string);
        lgd.FontSize = 7;
        lgd.NumColumns = 2;
        title(string(unique_dates(i)))
        xlabel('Index')
        ylabel(unit_label)
        hold off;
    end
    
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\', join(erase([lower(extractBefore(string(unit_label), '[')), 'days.fig'], ' '), '_')], '')  ], ''));
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\', join(erase([lower(extractBefore(string(unit_label), '[')), 'days.png'], ' '), '_')], '')  ], ''));
    end

end
