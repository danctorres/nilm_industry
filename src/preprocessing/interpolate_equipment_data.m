function [units_formated] = interpolate_equipment_data(date_unit_table, unit_name, metrics, selected_equipment_index, save)
    % Objective: Remove useless dates and insert missing samples for each equipment
    % Input: date_unit_table
    % Output: units_formated and equipment_formated.csv (table with all the datetimes and the active power value of each equipment)

    dates_only      = datetime(datestr(date_unit_table.Date, 'dd-mmm-yyyy'));
    unique_dates    = unique(dates_only);
    
    % Define the points used for interpolation
    dates_to_remove             = table2array(metrics(mean(table2array(metrics(:, 4:2:size(metrics, 2))), 2) < 10, 1));     % Remove useless dates

    filtered_dates_and_unit     = date_unit_table(~ismember(dates_only, dates_to_remove), :); % Remove days with mean median smaller than 500
    filtered_unique_dates       = unique_dates(~ismember(unique_dates, dates_to_remove), :);
    
    dates_complete = [];
    for i = 1:size(filtered_unique_dates, 1)
        date_year       = year(filtered_unique_dates(i));
        date_month      = month(filtered_unique_dates(i));
        date_day        = day(filtered_unique_dates(i));
        seconds         = 0:1:86400 - 1; % number of seconds in one day
        dates_complete  = cat(1, dates_complete, posixtime(datetime(date_year, date_month, date_day, 0, 0, seconds))');
    end
    
    date_dataset                = posixtime(filtered_dates_and_unit.Date);
    %%[diff, index_diff]          = setdiff(dates_complete, date_dataset);
    [~, index_date_dataset, ~]  = intersect(dates_complete, date_dataset);
    
    % Spline interpolation, using a cubic spline, alternatives: csaps / pchip
    unit_complete = zeros(size(dates_complete, 1), size(date_unit_table, 2) - 1);
    for i = 1:size(date_unit_table, 2) - 1
        [filtered_unit_no_outliers, TFrm]              = rmoutliers(filtered_dates_and_unit{:, i+1}, 'mean', 'ThresholdFactor', 3);      % remove outliers
        unit_complete(index_date_dataset(~TFrm), i)     = filtered_unit_no_outliers;
        
        [diff, index_diff]                              = setdiff(dates_complete, date_dataset(~TFrm));
        unit_complete(index_diff, i)                    = spline(date_dataset(~TFrm), filtered_unit_no_outliers, diff);
        unit_complete (unit_complete < 0) = 0;          % remove values smaller than zero, negative consumption not possible
    end
    
    units_formated = table(datetime(datenum(1970,1,1) + dates_complete/86400, 'ConvertFrom', 'datenum'), 'VariableNames', {'timestamp'});
    for i = 1:size(unit_complete, 2)
        units_formated.(join( [string(unit_name), sprintf('%i', selected_equipment_index(i))], '_')) = unit_complete(:, i);
    end

    % Save to file
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, called_file_name, ~] = fileparts(file_information.Filename);
        writetable(units_formated, join([erase(file_information.Filename,  join(['\src\preprocessing\', called_file_name, '.m'])), join( [join(['data\interim\', string(unit_name)], ''), 'formated.csv'], '_')], '\'));
        % units_formated.timestamp = datetime(date_complete, 'ConvertFrom', 'Posixtime');     % posix format
        % writetable(units_formated, join([erase(file_information.Filename, '\src\preprocessing\main.m'), join( [join(['\data\interim\', string(unit_name)], ''), 'posix.csv'], '_')], '\'));
    end
    
    % Debug
    % figure('units','normalized','outerposition',[0 0 1 1])
    % for i = 1 : size(equip_data, 2)
    %     subplot(size(equip_data, 2)/2, 2, i)
    %     plot(filtered_dates_and_power{:, i+1})
    %     title (sprintf('Equipment %i', i))
    %     xlabel ('Sample')
    %     ylabel('Power [W]')
    % end
    % figure('units','normalized','outerposition',[0 0 1 1])
    % for i = 1 : size(equip_data, 2)
    %     subplot(size(equip_data, 2)/2, 2, i)
    %     plot(unit_complete(:, i))
    %     title (sprintf('Equipment %i', i))
    %     xlabel ('Sample')
    %     ylabel('Power [W]')
    % end
end