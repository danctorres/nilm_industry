function [] = plot_data_select_day(data, date_index, unit, save)
    % Objective: Plot the active power values for all the equipment for one day
    % Input: data.csv
    % Output: subplots_data.fig, subplots_data.png

    % varargin{1} -> path
    % varargin{2} -> true for saving figure into files

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);

    % if (nargin > 0)
    %    data = varargin{1};
    % else
    %    data = readtable([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\data.csv']);
    % end

    dates_only = datetime(datestr(data.timestamp, 'dd-mmm-yyyy'));
    selected_date = dates_only(date_index);

    unit_label = string(unit);
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle(string(selected_date))
    [sharedvals, ~] = (ismember(dates_only, selected_date));
    for i = 2:size(data, 2)
        subplot((size(data, 2) - 1) / 2, 2, i - 1)
        plot(table2array(data(sharedvals, i)))

        table_collumn_name = data.Properties.VariableNames{i};

        title(['Equipment ', table_collumn_name(end)])
        xlabel('Index')
        ylabel(unit_label)
    end

    if (save == true)
        name_file = regexprep ( regexprep( lower(unit_label), '....$' , ''), ' ', '_');
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\', name_file, '_', string(selected_date), '.fig'], '')], '') );
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\', name_file, '_', string(selected_date), '.png'], '')], '') );
    end
end