function estimated = read_results_csv(struct_files)
    base_dir = {struct_files.folder};
    base_dir = base_dir(1);
    list_files = {struct_files.name};
    list_files = list_files(3:end);

    n_csv = size(list_files, 2);
    estimated = cell(1, n_csv);
    for i = 1:n_csv
        estimated{i} = readtable(join ([base_dir{1}, '\', string(list_files(i))], '' ));
    end
end