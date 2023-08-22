function [] = plot_data_per_equipment(data, unit, save)
    % Objective: plot all the data per equipment
    % Input: data (table, samples x equipment)
    % Output

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
    %sgtitle(regexprep( string(unit), '....$', ''), 'FontSize', 20);
    counter = 1;
    eq_labels = [1, 2, 3, 4, 7, 8];
    for i = 2:size(data, 2)
        %subplot( (size(data, 2) - 1) / 2, 2, i - 1);
        plot(data{:, i}, '.');

        table_collumn_name = data.Properties.VariableNames{i};

        %title(['Equipment ', table_collumn_name(end)], 'FontSize', 20);

        labels_eq{counter} = sprintf('Equipment %d', eq_labels(i - 1));
        counter = counter + 1;
        hold on
    end
    hold off;
    xlabel('Sample Index', 'FontSize', 20);
    ylabel('Active Power [W]', 'FontSize', 20);
    xticklabels = get(gca, 'XTick');
    set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
    yticklabels = get(gca, 'YTick');
    set(gca, 'yticklabels', yticklabels, 'FontSize', 20);
    legend(labels_eq, 'FontSize', 20);
    hLegend = gca;
    %title('Equipment Active Power', 'FontSize', 20);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
    eq_labels = [1, 2, 3, 4, 7, 8];
    for i = 2:size(data, 2)
        subplot( (size(data, 2) - 1) / 2, 2, i - 1);
        plot(data{:, i}, '.');
        title(sprintf('Equipment %d', eq_labels(i - 1)), 'FontSize', 20);
        xlabel('Sample Index', 'FontSize', 20);
        ylabel('Active Power [W]', 'FontSize', 20);
        xticklabels = get(gca, 'XTick');
        set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
        yticklabels = get(gca, 'YTick');
        set(gca, 'yticklabels', yticklabels, 'FontSize', 20);
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