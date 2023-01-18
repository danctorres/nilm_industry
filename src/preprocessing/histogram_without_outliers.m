function [output_counts_cell, output_edges_cell, output_bin_center, output_TF_cell] = histogram_without_outliers(data, minimum_prominence, bool_outl, save)
    % Objective: Create histograms of all the equipment active power samples
    % Input: active_power table, minimum_prominence for islocalmax,
    % bool_out (bool to remove outliers), save to save the histograms
    % Output: histogram images

    output_counts_cell      = cell(1, size(data, 2) - 1);
    output_edges_cell       = cell(1, size(data, 2) - 1);
    output_bin_center       = cell(1, size(data, 2) - 1);
    output_TF_cell          = cell(1, size(data, 2) - 1);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(data, 2) - 1
        subplot((size(data, 2) - 1) / 2, 2, i)
        data = table2array(data(:, i + 1));
        if bool_outl == true
            x_clean = rmoutliers( data(data >= 0), 'mean', 'ThresholdFactor', 3);
        else
            x_clean = data;
        end

        [counts, edges] = histcounts(x_clean, 100);
        histHandle      = histogram('BinEdges', edges, 'BinCounts', counts);
        bin_center      = histHandle.BinEdges + histHandle.BinWidth/2;
        bin_center      = bin_center(1:end - 1);
        hold on

        [TF, ~] = islocalmax([0, counts], 'MinProminence', minimum_prominence);

        output_counts_cell(i)   = {counts};
        output_edges_cell(i)    = {edges};
        output_bin_center(i)    = {bin_center};
        output_TF_cell(i)       = {TF(2:end)};

        plot(bin_center, counts, bin_center(TF(2:end)), counts(TF(2:end)),'r*')

        title(sprintf('Equipment %i', i))
        xlabel('Power [W]')
        ylabel('Number of samples')
        xL=xlim;
        yL=ylim;
        text(0.99*xL(2), 0.99*yL(2), sprintf('Number of peaks: %i', size(TF(TF ~= 0), 2)), 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top')
        hold off
    end
    
    if (save == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), ['\reports\figures\',  'histogram_power_no_outliers.fig']]);
        saveas(gcf, [erase(file_information.Filename, ['\src\preprocessing\', file_name, file_ext]), ['\reports\figures\',  'histogram_power_no_outliers.png']]);
    end
end