function agg_data = read_aggregate(dataset_name)
    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    cd([erase(file_information.Filename, ['\src\preprocessing\', dataset_name, '\', file_name, file_ext]), '\data\raw\', dataset_name]);
    
    file_list = dir;
    file_list = {file_list.name};
    file_list = file_list(3:end);

    agg_data = readtable(string(file_list(2)));

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    cd(erase(file_information.Filename, [file_name, file_ext]));

end