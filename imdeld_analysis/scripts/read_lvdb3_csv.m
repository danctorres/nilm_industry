% Objective: Read data from 'pelletizer-subcircuit.csv' (LVDB-2) and 'millingmachine-subcircuit.csv' (LVDB-3) and get active power for the same datetime values of table_datetime_active_power
% Input: equipment_path (path to equipment_formated.csv), lvdb3_path and lvdb3_path (path to \pelletizer-subcircuit.csv and millingmachine-subcircuit.csv)
% Output: lvdb3_formated and lvdb3_formated (table with the datetimes and the active power for the dates of lvdb3 and lvdb3 in common with equipment_formated)

function [lvdb3_complete_table] = read_lvdb3_csv(varargin)

% Duplicated code from
    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    
    if (nargin == 3)
        equipment_table         = readtable(varargin{2});
        lvdb3_original_table    = readtable(varargin{3});
    else
        equipment_table         = readtable([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\equipment_formated.csv']);
        lvdb3_original_table    = readtable([erase(file_information.Filename, ['\imdeld_analysis\scripts\', file_name, file_ext]), '\imdeld_dataset\millingmachine-subcircuit.csv']);
    end
    
    lvdb3_original_timestamps   = cell2mat(lvdb3_original_table.timestamp);
    lvdb3_timestamps_datetime   = datetime(lvdb3_original_timestamps(:, 1:end - 3));
    [sharedvals, ~]             = ismember(lvdb3_timestamps_datetime, equipment_table.timestamp);
    lvdb3_original_table        = table(lvdb3_timestamps_datetime(sharedvals), lvdb3_original_table.active_power(sharedvals), 'VariableNames', {'timestamp', 'active_power'});
    lvdb3_mean_values           = grpstats(lvdb3_original_table, 'timestamp', 'mean', 'DataVars', 'active_power');
    lvdb3_missing_dates_table   = table(lvdb3_mean_values.timestamp, lvdb3_mean_values.mean_active_power, 'VariableNames', {'timestamp', 'active_power'});
    clear lvdb3_mean_values;
    
    lvdb3_missing_dates_posix   = posixtime(lvdb3_missing_dates_table.timestamp);
    equipment_table_posix       = posixtime(equipment_table.timestamp);

    % ia = index pf data in equipment_table_posix that is not in lvdb3_missing_dates_posix
    [~, ia]                 = setdiff(equipment_table_posix, lvdb3_missing_dates_posix);
    [~, index_a, index_b]   = intersect(equipment_table_posix, lvdb3_missing_dates_posix);

    % interpolate
    active_power(index_a, 1)    = lvdb3_missing_dates_table.active_power(index_b);
    active_power(ia, 1)         = spline(lvdb3_missing_dates_posix, lvdb3_missing_dates_table.active_power, equipment_table_posix(ia));
    lvdb3_complete_table        = table(equipment_table.timestamp, active_power, 'VariableNames', {'timestamp', 'active_power'});
    
    if (nargin > 0 && varargin{1} == true)
        writetable(lvdb3_complete_table, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\lvdb3_formated.csv']);
    end

end