function [on_off_array] = calculate_on_off(equipment_formated, group_power_limit)
% Objective: Use the values of the first midpeak, state limite, to construct the on/off array
% Input: equipment_formated, group_power_limit(cell of the state limits)
% Output: on_off_array (array with with one if the equipment is in ON state for that sample otherwise is 0)

    on_off_array = zeros(size(equipment_formated, 1), size(equipment_formated, 2) - 1);
    for i = 1:size(group_power_limit, 1)
        lower_limit = group_power_limit{i, 1}(2);
        equipment_formated_array = table2array(equipment_formated(:, i + 1));
        on_off_array(:, i) = equipment_formated_array > lower_limit;
    end
    
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    for i = 1:size(group_power_limit, 1)
        subplot(size(group_power_limit, 1) / 2, 2, i)
        plot(on_off_array(:, i))
        legend('OFF', 'ON')
        xlabel('Second [s]')  
        ylabel('State')  
        title(sprintf('Equipment %i', i))
    end
end