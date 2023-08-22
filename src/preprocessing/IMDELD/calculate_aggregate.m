function [aggregate_table] = calculate_aggregate(lvdb2_table, lvdb3_table, units, save)
    % Objective: get aggregate data
    % Input: lvdb2_formated and lvdb3_formated paths
    % Output: aggregate_power

    % file_information = matlab.desktop.editor.getActive;
    % [~, file_name, file_ext] = fileparts(file_information.Filename);
    % lvdb2_table_path = [erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\data\interim\IMDELD\lvdb2_formated.csv'];
    % lvdb3_table_path = [erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), '\data\interim\IMDELD\lvdb3_formated.csv'];
    % lvdb2_table = readtable(lvdb2_table_path);
    % lvdb3_table = readtable(lvdb3_table_path);

    aggregate_table = table(lvdb2_table.timestamp, table2array(lvdb2_table(:, 2)) + table2array(lvdb3_table(:, 2)), 'VariableNames', {'timestamp', units});

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    plot(table2array(aggregate_table(:, 2)))
    title(['Aggregate ',  regexprep( units, '....$' , '')])
    xlabel('Samples')
    ylabel(units)

    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        name_file = regexprep ( regexprep( lower(units), '....$' , ''), ' ', '_');
        writetable(units_formated, join([erase(file_information.Filename,  join(['\src\preprocessing\IMDELD\', file_name, '.m'])), ['\data\interim\IMDELD\aggregate_', name_file, '.csv']], '\'));
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), ['\reports\figures\aggregate_',  name_file, '.fig']], '') );
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), ['\reports\figures\aggregate_',  name_file, '.png']], '') );
    end

    % Debug
    % equipment_table = readtable([erase(file_information.Filename, ['\scripts\' file_name file_ext]) '\results\data\equipment_formated.csv']);
    % name_collumn = cell(1, size(equipment_table, 2)-1);
    % for i = 1:size(equipment_table, 2) - 1
    %     name_collumn{i} = sprintf('Active_Power_Eq_%i', i);
    % end
    %
    % sum_equipment = sum(equipment_table{:, name_collumn}, 2);
    %
    % figure('units','normalized','outerposition',[0, 0, 1, 1])
    % plot(sum_equipment)
end
