function [] = plot_data_per_equipment(data, unit, save)
    % Objective: plot all the data per equipment
    % Input: data (table, samples x equipment)
    % Output

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(data, 2) - 1
        subplot( (size(data, 2) - 1) / 2, 2, i)
        plot(data{:, i + 1})
        title(sprintf('Equipment %i', i))
        xlabel('Index')
        ylabel(string(unit))
    end
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_', string(unit), '.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_', string(unit), '.png']);
    end
end