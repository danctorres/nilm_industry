% Objective: Read data from 'pelletizer-subcircuit.csv' (LVDB-2) and 'millingmachine-subcircuit.csv' (LVDB-3) and get active power for the same datetime values of table_datetime_active_power
% Input: equipment_path (path to equipment_formated.csv), lvdb2_path and lvdb3_path (path to \pelletizer-subcircuit.csv and millingmachine-subcircuit.csv)
% Output: lvdb2_formated and lvdb3_formated (table with the datetimes and the active power for the dates of lvdb2 and lvdb3 in common with equipment_formated)

function [lvdb2_complete_table] = read_lvdb2_csv(varargin)

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);

if (nargin == 3)
    equipment_table         = readtable(varargin{2});
    lvdb2_original_table    = readtable(varargin{3});
else
    equipment_table         = readtable([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\equipment_formated.csv']);
    lvdb2_original_table    = readtable([erase(file_information.Filename, ['\imdeld_analysis\scripts\', file_name, file_ext]), '\imdeld_dataset\pelletizer-subcircuit.csv']);
end

lvdb2_original_timestamps   = cell2mat(lvdb2_original_table.timestamp);
lvdb2_timestamps_datetime   = datetime(lvdb2_original_timestamps(:, 1:end - 3));
[sharedvals, ~]             = ismember(lvdb2_timestamps_datetime, equipment_table.timestamp);
lvdb2_original_table        = table(lvdb2_timestamps_datetime(sharedvals), lvdb2_original_table.active_power(sharedvals), 'VariableNames', {'timestamp', 'active_power'});
lvdb2_mean_values           = grpstats(lvdb2_original_table, 'timestamp', 'mean', 'DataVars', 'active_power');
lvdb2_missing_dates_table   = table(lvdb2_mean_values.timestamp, lvdb2_mean_values.mean_active_power, 'VariableNames', {'timestamp', 'active_power'});
clear lvdb2_mean_values;

lvdb2_missing_dates_posix   = posixtime(lvdb2_missing_dates_table.timestamp);
equipment_table_posix       = posixtime(equipment_table.timestamp);

% ia = index pf data in equipment_table_posix that is not in lvdb2_missing_dates_posix
[~, ia]                 = setdiff(equipment_table_posix, lvdb2_missing_dates_posix);
[~, index_a, index_b]   = intersect(equipment_table_posix, lvdb2_missing_dates_posix);

% interpolate
active_power(index_a, 1)    = lvdb2_missing_dates_table.active_power(index_b);
active_power(ia, 1)         = spline(lvdb2_missing_dates_posix, lvdb2_missing_dates_table.active_power, equipment_table_posix(ia));
lvdb2_complete_table        = table(equipment_table.timestamp, active_power, 'VariableNames', {'timestamp', 'active_power'});

if (nargin > 0 && varargin{1} == true)
    writetable(lvdb2_complete_table, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\lvdb2_formated.csv']);
end

end