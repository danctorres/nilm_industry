function [PF] = calculate_PF(active_power, apparent_power, selected_equipment_index)

    PF = active_power(:, 1);
    for i = 1:size(active_power, 2) - 1
        columns_fp(i, :) = ['power_factor', sprintf('_%i', selected_equipment_index(i))];
    end
    PF =  [PF array2table(table2array(active_power(:, 2:end)) ./ table2array(apparent_power(:, 2:end)), 'VariableNames', string(columns_fp))];
end