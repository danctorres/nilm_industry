function [] = histogram_state_peak_equipment(equipment_formated, group_power_limit_cell)
% Objective: plot the histogram of each state of the equipment based on the values of the active power indexed by the peaks and in betweens of the peaks
% Inputs: equipment_formated, group_power_limit_cell (cell of the edge values of each state) per equipment
% Ouputs: histograms

    for i = 1:size(group_power_limit_cell, 1)
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
        sgtitle(sprintf('Equipment % i', i));
        
        inner_loop_count = size(group_power_limit_cell, 2);
        while(isempty(group_power_limit_cell{i, inner_loop_count}))
            inner_loop_count = inner_loop_count - 1;
        end
        for j = 1:inner_loop_count
            lower_limit = group_power_limit_cell{i, j}(1);
            upper_limit = group_power_limit_cell{i, j}(2);
    
            equipment_formated_array = table2array(equipment_formated(:, i + 1));
            groups_values = equipment_formated_array(equipment_formated_array > lower_limit & equipment_formated_array < upper_limit);
    
            subplot(size(group_power_limit_cell, 2), 1, j);
            histogram(groups_values, 100)
            title(sprintf('State %i', j));
            xlabel('Power [W]')
            ylabel('Number of samples')
        end
    end
end