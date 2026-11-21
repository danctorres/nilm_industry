function [aggregate_data] = calculate_aggregate_all_feature(raw_dir, timestamp, selected_equipment_index, smoothing_window)
    % Objective: Aggregate features at the given timestamps: LVDB-2, plus LVDB-3 when machines 5 and 6 (milling machines) are selected
    % Input: raw_dir (folder with the LVDB csv files), timestamp, selected_equipment_index, smoothing_window (movmean window in samples)
    % Output: aggregate_data (table: timestamp, active, reactive and apparent power, current, voltage, power factor)

    lvdb2 = fullfile(raw_dir, 'pelletizer-subcircuit.csv');
    lvdb3 = fullfile(raw_dir, 'millingmachine-subcircuit.csv');

    active_pow      = read_lvdb_csv(lvdb2, timestamp, 'active_power', smoothing_window);
    reactive_pow    = read_lvdb_csv(lvdb2, timestamp, 'reactive_power', smoothing_window);
    apparent_pow    = read_lvdb_csv(lvdb2, timestamp, 'apparent_power', smoothing_window);
    curr            = read_lvdb_csv(lvdb2, timestamp, 'current', smoothing_window);
    volt            = read_lvdb_csv(lvdb2, timestamp, 'voltage', smoothing_window);

    if (any(ismember(selected_equipment_index, 5) == 1) && any(ismember(selected_equipment_index, 6) == 1))
        buff_table = read_lvdb_csv(lvdb3, timestamp, 'active_power', smoothing_window);
        active_pow.('active_power')         = active_pow.('active_power') + buff_table.('active_power');
        clear buff_table;
        buff_table = read_lvdb_csv(lvdb3, timestamp, 'reactive_power', smoothing_window);
        reactive_pow.('reactive_power')     = reactive_pow.('reactive_power') + buff_table.('reactive_power');
        clear buff_table;
        buff_table = read_lvdb_csv(lvdb3, timestamp, 'apparent_power', smoothing_window);
        apparent_pow.('apparent_power')     = apparent_pow.('apparent_power') + buff_table.('apparent_power');
        clear buff_table;
        buff_table = read_lvdb_csv(lvdb3, timestamp, 'current', smoothing_window);
        curr.('current')                    = curr.('current') + buff_table.('current');
        clear buff_table;
        buff_table = read_lvdb_csv(lvdb3, timestamp, 'voltage', smoothing_window);
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
end
