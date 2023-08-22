function [lvdb_complete_table] = read_lvdb_csv(units_data, units, lvdb_number, save)
    % Objective: Read data from 'pelletizer-subcircuit.csv' (LVDB-2) and 'millingmachine-subcircuit.csv' (LVDB-3) and get active power for the same datetime values of table_datetime_active_power
    % Input: equipment_path (path to equipment_formated.csv), lvdb_path and lvdb3_path (path to \pelletizer-subcircuit.csv and millingmachine-subcircuit.csv)
    % Output: lvdb_formated and lvdb3_formated (table with the datetimes and the active power for the dates of lvdb and lvdb3 in common with equipment_formated)

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);

    % equipment_table             = readtable([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\data\interim\IMDELD\equipment_formated.csv']);
    if (lvdb_number == 2)
        lvdb_original_table     = readtable([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\data\raw\IMDELD\pelletizer-subcircuit.csv']);
    elseif (lvdb_number == 3)
        lvdb_original_table     = readtable([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\data\raw\IMDELD\millingmachine-subcircuit.csv']);
    end

    lvdb_original_timestamps    = cell2mat(lvdb_original_table.timestamp);
    lvdb_timestamps_datetime    = datetime(lvdb_original_timestamps(:, 1:end - 3));

%     % Plot original data
%     figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
%     plot(lvdb_timestamps_datetime, lvdb_original_table.active_power, '.');
%     xlabel('Datestamp', 'FontSize', 20);
%     ylabel('Active Power [W]', 'FontSize', 20);
%     %title('Aggregate Active Power', 'FontSize', 20);
%     xticklabels = get(gca, 'xticklabels');
%     set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
%     yticklabels = get(gca, 'YTick');
%     set(gca, 'yticklabels', yticklabels, 'FontSize', 20);

    [sharedvals, ~]             = ismember(lvdb_timestamps_datetime, units_data);
    lvdb_unit_column            = lvdb_original_table.(string(units));
    lvdb_original_table         = table(lvdb_timestamps_datetime(sharedvals), lvdb_unit_column(sharedvals), 'VariableNames', {'timestamp', units});

    % Delete NaN values
    lvdb_original_table         = rmmissing(lvdb_original_table);

    lvdb_mean_values            = grpstats(lvdb_original_table, 'timestamp', 'mean', 'DataVars', string(units));
    lvdb_missing_dates_table    = table(lvdb_mean_values.timestamp, lvdb_mean_values.(join(['mean', string(units)], '_')), 'VariableNames', {'timestamp', units});
    clear lvdb_mean_values;

    lvdb_missing_dates_posix    = posixtime(lvdb_missing_dates_table.timestamp);
    equipment_table_posix       = posixtime(units_data);


    lvdb_unit                       = lvdb_missing_dates_table.(string(units));
    % remove outliers
    % [lvdb_no_outliers, TFrm]        = rmoutliers(lvdb_unit, 'mean', 'ThresholdFactor', 3);
    % [~, idx_miss]                   = setdiff(equipment_table_posix, lvdb_missing_dates_posix(~TFrm));     % timestamps missing from the lvdb data
    % [~, index_a, index_b]           = intersect(equipment_table_posix, lvdb_missing_dates_posix(~TFrm));   % timestamps in the lvdb data
    lvdb_no_outliers                = movmean(lvdb_unit, 1500);
    [~, idx_miss]                   = setdiff(equipment_table_posix, lvdb_missing_dates_posix(:));     % timestamps missing from the lvdb data
    [~, index_a, index_b]           = intersect(equipment_table_posix, lvdb_missing_dates_posix(:));   % timestamps in the lvdb data

    % interpolate
    unit_values(index_a, 1)         = lvdb_no_outliers(index_b);
    unit_values(idx_miss, 1)        = spline(lvdb_missing_dates_posix, lvdb_no_outliers, equipment_table_posix(idx_miss));
    unit_values(unit_values < 0)    = 0;
    lvdb_complete_table             = table(units_data, unit_values, 'VariableNames', {'timestamp', units});

    if (save == true)
        writetable(lvdb_complete_table, join([erase(file_information.Filename,  join(['\src\preprocessing\IMDELD\', file_name, '.m'])), join( [join(['data\interim\IMDELD\', string(lvdb_number)], ''), 'formated.csv'], '_')], '\'));
    end
end
