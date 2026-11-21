function tables = read_results_csv(pattern)
    % Objective: read every csv file matching pattern (wildcards allowed), in alphabetical file order
    % Input: pattern (e.g. fullfile(results_dir, 'estimated_active_power*.csv'))
    % Output: tables (cell array, one table per file)

    files = dir(pattern);
    assert(~isempty(files), 'No file matches %s', pattern);
    tables = cell(1, numel(files));
    for i = 1:numel(files)
        tables{i} = readtable(fullfile(files(i).folder, files(i).name));
    end
end
