function [output] = read_interim_data(file_name)
    % Function to easily read data from interim
    % Input file name in interim

    file_information = matlab.desktop.editor.getActive;
    [~, called_file_name, file_ext] = fileparts(file_information.Filename);
    output = readtable(join([erase(file_information.Filename,  join(['\src\preprocessing\', called_file_name, '.m'])), join( [join(['data\interim\', string(file_name)], '')])], '\'));
end