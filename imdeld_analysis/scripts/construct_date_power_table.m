% Objective: Construct a table with the timestamps and active power values of the eight equipment
% Input: equip_data, useful_common_timestamps
% Output: date_active_power (table with timestamp and active power values for eight equipment)

function [date_active_power] = construct_date_power_table(equip_data, useful_common_timestamps, varargin)
    date_active_power = table(useful_common_timestamps, 'VariableNames', {'Date'});
    for i = 1:size(equip_data, 2)
        table_eq = equip_data{i};
        mean_values = grpstats(table_eq, 'timestamp', 'mean', 'DataVars', 'active_power');
        datetime_values = cell2mat(mean_values.timestamp);
        dates_only = unique(datetime(datetime_values(:, 1:end-3)));
        [sharedvals, ~] = ismember(dates_only, useful_common_timestamps);
    
        active_power = mean_values.mean_active_power(sharedvals);
        date_active_power.(sprintf('active_power_eq_%i', i)) = active_power;
    end

    if (nargin == 1 && varargin{1} == true)
        figure('units','normalized','outerposition',[0 0 1 1])
        for i = 1 : size(equip_data, 2)
            subplot(size(equip_data, 2)/2, 2, i)
            plot(date_active_power{:, i+1})
            title (sprintf('Equipment %i', i))
            xlabel ('Index')
            ylabel('Power [W]')
        end
        
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\' file_name file_ext]) '\results\images\dates_active_power.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\' file_name file_ext]) '\results\images\dates_active_power.png']);
    end
end