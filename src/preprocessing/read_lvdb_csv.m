function [lvdb_complete_table] = read_lvdb_csv(units_data, units, lvdb_number, selected_equipment_index, save)
    % Objective: Read data from 'pelletizer-subcircuit.csv' (LVDB-2) and 'millingmachine-subcircuit.csv' (LVDB-3) and get active power for the same datetime values of table_datetime_active_power
    % Input: equipment_path (path to equipment_formated.csv), lvdb_path and lvdb3_path (path to \pelletizer-subcircuit.csv and millingmachine-subcircuit.csv)
    % Output: lvdb_formated and lvdb3_formated (table with the datetimes and the active power for the dates of lvdb and lvdb3 in common with equipment_formated)

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    
    % equipment_table             = readtable([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\data\interim\equipment_formated.csv']);
    missing_eq                      = false;
    equipment_table                 = units_data;
    if (lvdb_number == 2)
        lvdb_original_table         = readtable([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\data\raw\pelletizer-subcircuit.csv']);
    elseif (lvdb_number == 3)
        if (any(ismember(selected_equipment_index, 5) == 1) && any(ismember(selected_equipment_index, 6) == 1))
            lvdb_original_table     = readtable([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\data\raw\millingmachine-subcircuit.csv']);
        else
            lvdb_complete_table     =  table(zeros(size(units_data, 1), 1), zeros(size(units_data, 1), 1), 'VariableNames', {'timestamp', units});
            missing_eq = true;
        end
    end

    if (missing_eq == false)
        lvdb_original_timestamps    = cell2mat(lvdb_original_table.timestamp);
        lvdb_timestamps_datetime    = datetime(lvdb_original_timestamps(:, 1:end - 3));
        [sharedvals, ~]             = ismember(lvdb_timestamps_datetime, equipment_table.timestamp);
        lvdb_unit_column            = lvdb_original_table.(string(units));
        lvdb_original_table         = table(lvdb_timestamps_datetime(sharedvals), lvdb_unit_column(sharedvals), 'VariableNames', {'timestamp', units});
        lvdb_mean_values            = grpstats(lvdb_original_table, 'timestamp', 'mean', 'DataVars', string(units));
        lvdb_missing_dates_table    = table(lvdb_mean_values.timestamp, lvdb_mean_values.(join(['mean', string(units)], '_')), 'VariableNames', {'timestamp', units});
        clear lvdb_mean_values;
        
        lvdb_missing_dates_posix    = posixtime(lvdb_missing_dates_table.timestamp);
        equipment_table_posix       = posixtime(equipment_table.timestamp);
    
        
        
        % ia = index pf data in equipment_table_posix that is not in lvdb_missing_dates_posix
        [~, ia]                 = setdiff(equipment_table_posix, lvdb_missing_dates_posix);
        [~, index_a, index_b]   = intersect(equipment_table_posix, lvdb_missing_dates_posix);
        
        % interpolate
        lvdb_missing_dates_column   = lvdb_missing_dates_table.(string(units));
        unit_values(index_a, 1)     = lvdb_missing_dates_column(index_b);
        unit_values(ia, 1)          = spline(lvdb_missing_dates_posix, lvdb_missing_dates_column, equipment_table_posix(ia));
        lvdb_complete_table         = table(equipment_table.timestamp, unit_values, 'VariableNames', {'timestamp', units});
    end

    if (save == true)
        writetable(lvdb_complete_table, join([erase(file_information.Filename,  join(['\src\preprocessing\', called_file_name, '.m'])), join( [join(['data\interim\', string(lvdb_number)], ''), 'formated.csv'], '_')], '\'));
    end
end