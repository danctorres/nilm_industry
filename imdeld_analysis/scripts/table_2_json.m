% Objective: Convert table to json file template
% Input: table
% Output: json file

function [] = table_2_json(table_variable)
    struct = table2struct(table_variable);
    jsonString = jsonencode(struct);

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);

    fid = fopen([erase(file_information.Filename, ['\scripts\' file_name file_ext]) ['\results\data\' inputname(1) '.json']], 'w');
    fprintf(fid, '%s', jsonString);
    fclose(fid);
end