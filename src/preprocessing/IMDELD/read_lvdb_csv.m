function [lvdb_complete_table] = read_lvdb_csv(file, units_data, units, smoothing_window)
    % Objective: Read one unit of an LVDB file ('pelletizer-subcircuit.csv' is LVDB-2, 'millingmachine-subcircuit.csv' is LVDB-3), smooth it and interpolate it at the timestamps units_data
    % Input: file (path of the LVDB csv), units_data (datetime array), units (column name), smoothing_window (movmean window in samples)
    % Output: lvdb_complete_table (table with the timestamps units_data and the unit values)

    lvdb_original_table         = readtable(file);
    lvdb_original_timestamps    = cell2mat(lvdb_original_table.timestamp);
    lvdb_timestamps_datetime    = datetime(lvdb_original_timestamps(:, 1:end - 3));

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
    lvdb_no_outliers                = movmean(lvdb_unit, smoothing_window);
    [~, idx_miss]                   = setdiff(equipment_table_posix, lvdb_missing_dates_posix(:));     % timestamps missing from the lvdb data
    [~, index_a, index_b]           = intersect(equipment_table_posix, lvdb_missing_dates_posix(:));   % timestamps in the lvdb data

    % interpolate
    unit_values(index_a, 1)         = lvdb_no_outliers(index_b);
    unit_values(idx_miss, 1)        = spline(lvdb_missing_dates_posix, lvdb_no_outliers, equipment_table_posix(idx_miss));
    unit_values(unit_values < 0)    = 0;
    lvdb_complete_table             = table(units_data, unit_values, 'VariableNames', {'timestamp', units});
end
