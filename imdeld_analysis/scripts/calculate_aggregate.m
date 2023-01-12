function [aggregate_table] = calculate_aggregate(varargin)
    % Objective: get aggregate data
    % Input: lvdb2_formated and lvdb3_formated paths
    % Output: aggregate_power

    file_information = matlab.desktop.editor.getActive;
    [~, file_name, file_ext] = fileparts(file_information.Filename);
    if (nargin == 3)
        aggregate_table = table(varargin{2}.timestamp,  sum(varargin{2}.active_power, 2) +  sum(varargin{3}.active_power, 2), 'VariableNames', {'timestamp', 'active_power'});
    else
        lvdb2_table_path = [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\lvdb2_formated.csv'];
        lvdb3_table_path = [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\lvdb3_formated.csv'];
        
        lvdb2_table = readtable(lvdb2_table_path);
        lvdb3_table = readtable(lvdb3_table_path);
        
        aggregate_table = table(lvdb2_table.timestamp, lvdb2_table.active_power+lvdb3_table.active_power, 'VariableNames', {'timestamp', 'active_power'});
    end

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    plot(aggregate_table.active_power)
    title('Aggregate Power')
    xlabel('Second [s]')
    ylabel('Active Power [W]')
    
    if (nargin > 0 && varargin{1} == true)
        writetable(aggregate_table, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\aggregate_table.csv']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\aggregate_power.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\aggregate_power.png']);
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