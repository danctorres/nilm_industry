function [] = histogram_equipment_original(equip_data, save)
    % Objective: Create histograms of all the equipment active power samples for selected days
    % Input: equip_data
    % Output: histogram images

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(equip_data, 2)
        subplot(size(equip_data, 2) / 2, 2, i)
        eq_table = equip_data{i};
        histogram( table2array(eq_table(:, 2)));
        title(sprintf('Equipment %i', i))
        xlabel('Power [W]')
        ylabel('Number of samples')
    end
    
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), ['\reports\figures\',  'histogram_original_power.fig']]);
        saveas(gcf, [erase(file_information.Filename, ['\src\preprocessing\IMDELD\', file_name, file_ext]), ['\reports\figures\',  'histogram_original_power.png']]);
    end
end