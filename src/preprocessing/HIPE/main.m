close all; clear; clc;

% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd([erase(file_dir, 'HIPE'), 'IMDELD']);

equip_data = read_equipment_csv('HIPE');

cd(file_dir);
agg_data = read_aggregate('HIPE');

% ToDo: Finish formating script