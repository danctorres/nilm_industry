function [PF] = calculate_PF(current_formated, voltage_formated, selected_equipment_index)
    
    PF = current_formated(:, 1);
    for i = 1:size(voltage_formated, 2) - 1
        columns_fp(i, :) = ['power_factor', sprintf('_%i', selected_equipment_index(i))];
    end
    PF =  [PF array2table(table2array(current_formated(:, 2:end)) .* table2array(voltage_formated(:, 2:end)), 'VariableNames', string(columns_fp))];
end