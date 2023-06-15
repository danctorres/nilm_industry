function [] = plot_data_per_equipment(data, unit, save)
    % Objective: plot all the data per equipment
    % Input: data (table, samples x equipment)
    % Output

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle(regexprep( string(unit), '....$', ''))
    for i = 2:size(data, 2)
        subplot( (size(data, 2) - 1) / 2, 2, i - 1)
        plot(data{:, i})

        table_collumn_name = data.Properties.VariableNames{i};

        title(['Equipment ', table_collumn_name(end)])
        xlabel('Index')
        ylabel(string(unit))
    end
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_', string(unit), '.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\dates_', string(unit), '.png']);

        name_file = regexprep ( regexprep( lower(unit_label), '....$' , ''), ' ', '_');
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\all_days', name_file, '_', '.fig'], '')], '') );
        saveas(gcf, join([erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), join(['\reports\figures\all_days', name_file, '_', '.png'], '')], '') );
    end
end