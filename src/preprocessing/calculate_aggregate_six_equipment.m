 function [aggregate_data] = calculate_aggregate_six_equipment(timestamp, save)
       
    active_pow = read_lvdb_csv(timestamp, 'active_power', 2, 0, false);     % value 0 isn't needed, is just a required input
    reactive_pow = read_lvdb_csv(timestamp, 'reactive_power', 2, 0, false);
    apparent_pow = read_lvdb_csv(timestamp, 'apparent_power', 2, 0, false);
    curr = read_lvdb_csv(timestamp, 'current', 2, 0, false);
    volt = read_lvdb_csv(timestamp, 'voltage', 2, 0, false);

    power_factor = calculate_PF(active_pow, apparent_pow, [1, 2, 3, 4, 7, 8]);

    unit_names = {'timestamp', 'active_power', 'reactive_power', 'apparent_power', 'current', 'voltage', 'power_factor'};
    aggregate_data = table(timestamp, active_pow.active_power, reactive_pow.reactive_power, apparent_pow.apparent_power, curr.current, volt.voltage, power_factor.power_factor_1, ...
        'VariableNames', unit_names);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle('Aggregate data')
    for i = 2:size(aggregate_data, 2)
        subplot((size(aggregate_data, 2) - 1) / 2, 2, i - 1)
        plot(table2array(aggregate_data(:, i)))
        title(regexprep(unit_names(i), '_', ' '))
    end

    if save == true
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\reports\figures\aggregate_table.fig']), '');
    end
end