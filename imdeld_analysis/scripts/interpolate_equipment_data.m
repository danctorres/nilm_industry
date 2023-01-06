% Objective: Remove the 30-March-2018 from the useful_common_timestamps and insert missing samples for each equipment
% Input: equip_data, date_active_power dates dates_only
% Output: equipment_formated.csv (table with all the datetimes and the active power value of each equipment)

function [equipment_formated] = interpolate_equipment_data(date_active_power, varargin)
    dates_only = datetime(datestr(date_active_power.Date, 'dd-mmm-yyyy'));
    unique_dates = unique(dates_only);
    filtered_dates_and_power = date_active_power(dates_only ~= unique_dates(end-1), :); % Remove the 30-Mar-2018 -> unique_dates(end - 1)
    
    % Define the points used for interpolation
    filtered_date_active_power = date_active_power(dates_only ~= unique_dates(end-1), :);
    filtered_unique_dates = unique_dates(1:end-2);
    filtered_unique_dates = cat(1, filtered_unique_dates, unique_dates(end));
    
    dates_complete = [];
    for i = 1:size(filtered_unique_dates, 1)
        date_year = year(filtered_unique_dates(i));
        date_month = month(filtered_unique_dates(i));
        date_day = day(filtered_unique_dates(i));
        seconds = 0:1:86400 - 1; % number of seconds in one day
        dates_complete = cat(1, dates_complete, posixtime(datetime(date_year, date_month, date_day, 0, 0, seconds))');
    end
    
    date_dataset = posixtime(filtered_dates_and_power.Date);
    [diff, index_diff] = setdiff(dates_complete, date_dataset);
    [~, index_date_dataset, ~] = intersect(dates_complete, date_dataset);
    
    % Spline interpolation
    active_power_complete = zeros(size(dates_complete, 1), size(equip_data, 2));
    for i = 1:size(equip_data, 2)
        y = filtered_date_active_power{:, i+1};
        active_power_complete(index_date_dataset, i) = y;
        yi = spline(date_dataset, y, diff); % Interpolate the data using a cubic spline, alternatives: csaps / pchip
        active_power_complete(index_diff, i) = yi;
    end
    
    date_complete = sort(cat(1, date_dataset, diff), 'ascend');
    table_useful = table(date_complete(:), 'VariableNames', {'timestamp'});
    for i = 1:size(active_power_complete, 2)
        name_collumn = sprintf('Active_Power_Eq_%i', i);
        table_useful.(name_collumn) = active_power_complete(:, i);
    end
    
    file_information = matlab.desktop.editor.getActive;
    writetable(table_useful, [erase(file_information.Filename, '\scripts\main.m') '\results\data\equipment_posix_formated.csv']);
    
    % datetime format
    equipment_formated = table_useful;
    equipment_formated.timestamp = datetime(date_complete, 'ConvertFrom', 'Posixtime');
    
    if (nargin == 1 && varargin{1} == true)
        writetable(equipment_formated, [erase(file_information.Filename, '\scripts\main.m') '\results\data\equipment_formated.csv']);
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
    %     plot(active_power_complete(:, i))
    %     title (sprintf('Equipment %i', i))
    %     xlabel ('Sample')
    %     ylabel('Power [W]')
    % end
end