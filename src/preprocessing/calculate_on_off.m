function [on_off_array] = calculate_on_off(data, group_power_limit, save)
    % Objective: Use the values of the first midpeak, state limite, to construct the on/off array
    % Input: equipment_formated, group_power_limit (cell of the state limits) or uses as threshold
    % Output: on_off_array (array with with one if the equipment is in ON state for that sample otherwise is 0)

    on_off_array = zeros(size(data, 1), size(data, 2) - 1);
    for i = 1:size(data, 2) - 1
        if (size(group_power_limit, 1) == 1 && size(group_power_limit, 2) == 1)
            lower_limit = group_power_limit;
        else
            lower_limit = group_power_limit{i, 1}(2);
        end
        equipment_formated_array = table2array(data(:, i + 1));
        on_off_array(:, i) = equipment_formated_array > lower_limit;
    end
    
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    sgtitle('Equipment ON/OFF states')
    for i = 1:size(data, 2) - 1
        subplot((size(data, 2) - 1)/ 2, 2, i)
        plot(on_off_array(:, i))
        xlabel('Samples')
        ylabel('State [ON/OFF]')
        title(sprintf('Equipment %i', i))
    end

    if save == true
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        writematrix(on_off_array, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\interim\IMDELD\on_off.csv'], '\'));
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\reports\figures\on_off.fig'], '') );
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), '\reports\figures\on_off.png'], '') );
    end
end
