function [aggregate_data] = calculate_aggregate_all_feature(timestamp, selected_equipment_index, save)
    active_pow      = read_lvdb_csv(timestamp, 'active_power', 2, false);
    reactive_pow    = read_lvdb_csv(timestamp, 'reactive_power', 2, false);
    apparent_pow    = read_lvdb_csv(timestamp, 'apparent_power', 2, false);
    curr            = read_lvdb_csv(timestamp, 'current', 2, false);
    volt            = read_lvdb_csv(timestamp, 'voltage', 2, false);

    if (any(ismember(selected_equipment_index, 5) == 1) && any(ismember(selected_equipment_index, 6) == 1))
        buff_table = read_lvdb_csv(timestamp, 'active_power', 3, false);
        active_pow.('active_power')         = active_pow.('active_power') + buff_table.('active_power');
        clear buff_table;
        buff_table = read_lvdb_csv(timestamp, 'reactive_power', 3, false);
        reactive_pow.('reactive_power')     = reactive_pow.('reactive_power') + buff_table.('reactive_power');
        clear buff_table;
        buff_table = read_lvdb_csv(timestamp, 'apparent_power', 3, false);
        apparent_pow.('apparent_power')     = apparent_pow.('apparent_power') + buff_table.('apparent_power');
        clear buff_table;
        buff_table = read_lvdb_csv(timestamp, 'current', 3, false);
        curr.('current')                    = curr.('current') + buff_table.('current');
        clear buff_table;
        buff_table = read_lvdb_csv(timestamp, 'voltage', 3, false);
        volt.('voltage')                    = volt.('voltage') + buff_table.('voltage');
        clear buff_table;
    end

    power_factor = calculate_PF(active_pow, apparent_pow, selected_equipment_index);

    unit_names = {'timestamp', 'active_power', 'reactive_power', 'apparent_power', 'current', 'voltage', 'power_factor'};
    aggregate_data = table(timestamp, active_pow.active_power, reactive_pow.reactive_power, apparent_pow.apparent_power, curr.current, volt.voltage, power_factor.power_factor_1, ...
        'VariableNames', unit_names);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle('Aggregate data')
    for i = 2:size(aggregate_data, 2)
        subplot((size(aggregate_data, 2) - 1) / 2, 2, i - 1)
        plot(table2array(aggregate_data(:, i)))
        title(regexprep(unit_names(i), '_', ' '))
        xlabel('samples')
        ylabel(strrep(aggregate_data.Properties.VariableNames(i), '_', ' '));
    end

    if save == true
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\reports\figures\aggregate_table.fig']), '');
    end
end