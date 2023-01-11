% Objective: Construct a table with the timestamps and active power values of the eight equipment
% Input: equip_data, useful_common_timestamps
% Output: date_voltage (table with timestamp and active power values for eight equipment)

function [date_voltage] = construct_date_voltage_table(equip_data, useful_common_timestamps, save)
    date_voltage = table(useful_common_timestamps, 'VariableNames', {'Date'});
    for i = 1:size(equip_data, 2)
        table_eq            = equip_data{i};
        mean_values         = grpstats(table_eq, 'timestamp', 'mean', 'DataVars', 'voltage');
        datetime_values     = cell2mat(mean_values.timestamp);
        dates_only          = unique(datetime(datetime_values(:, 1:end - 3)));
        [sharedvals, ~]     = ismember(dates_only, useful_common_timestamps);
    
        voltage = mean_values.mean_voltage(sharedvals);
        date_voltage.(sprintf('voltage_eq_%i', i)) = voltage;
    end
    
    if (save == true)
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
        for i = 1:size(equip_data, 2)
            subplot(size(equip_data, 2) / 2, 2, i)
            plot(date_voltage{:, i + 1})
            title(sprintf('Equipment %i', i))
            xlabel('Index')
            ylabel('Power [W]')
        end
    
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_voltage.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_voltage.png']);
    end
end