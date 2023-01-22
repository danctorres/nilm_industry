function [aggregate_table] = calculate_aggregate(lvdb2_table, lvdb3_table, save)
    % Objective: get aggregate data
    % Input: lvdb2_formated and lvdb3_formated paths
    % Output: aggregate_power

    % file_information = matlab.desktop.editor.getActive;
    % [~, file_name, file_ext] = fileparts(file_information.Filename);
    % lvdb2_table_path = [erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\data\interim\lvdb2_formated.csv'];
    % lvdb3_table_path = [erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\data\interim\lvdb3_formated.csv'];    
    % lvdb2_table = readtable(lvdb2_table_path);
    % lvdb3_table = readtable(lvdb3_table_path);

    aggregate_table = table(lvdb2_table.timestamp, lvdb2_table.active_power + lvdb3_table.active_power, 'VariableNames', {'timestamp', 'active_power'});
   
    if (save == true)
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
        plot(aggregate_table.active_power)
        title('Aggregate Power')
        xlabel('Second [s]')
        ylabel('Active Power [W]')

        writetable(units_formated, join([erase(file_information.Filename,  join(['\src\preprocessing\', called_file_name, '.m'])), 'data\interim\aggregate_power.csv'], '\'));
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\reports\figures\aggregate_power.fig'], '') );
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\reports\figures\aggregate_power.png'], '') );
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