function [output_counts_cell, output_edges_cell, output_bin_center, output_TF_cell] = histogram_without_outliers(varargin)
    % Objective: Create histograms of all the equipment active power samples for selected days
    % Input: equipment_formated
    % Output: histogram images

    equipment_formated = varargin{1};
    output_counts_cell      = cell(1, size(equipment_formated, 2) - 1);
    output_edges_cell       = cell(1, size(equipment_formated, 2) - 1);
    output_bin_center       = cell(1, size(equipment_formated, 2) - 1);
    output_TF_cell          = cell(1, size(equipment_formated, 2) - 1);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(equipment_formated, 2) - 1
        subplot((size(equipment_formated, 2) - 1) / 2, 2, i)
        data        = table2array(equipment_formated(:, i + 1));
        x_clean     = rmoutliers( data(data >= 0), 'mean', 'ThresholdFactor', 3);

        [counts, edges] = histcounts(x_clean);
        histHandle      = histogram('BinEdges', edges, 'BinCounts', counts);
        bin_center      = histHandle.BinEdges + histHandle.BinWidth/2;
        bin_center      = bin_center(1:end - 1);
        hold on

        % Find the peaks in the histogram        
        [TF, ~] = islocalmax([0, counts], 'MinProminence', 2000);

        output_counts_cell(i)   = {counts};
        output_edges_cell(i)    = {edges};
        output_bin_center(i)    = {bin_center};
        output_TF_cell(i)       = {TF(2:end)};

        plot(bin_center, counts, bin_center(TF(2:end)), counts(TF(2:end)),'r*')

        [TF, ~] = islocalmax([0, counts], 'MinProminence', 2000);


        title(sprintf('Equipment %i', i))
        xlabel('Power [W]')
        ylabel('Number of samples')
        xL=xlim;
        yL=ylim;
        text(0.99*xL(2), 0.99*yL(2), sprintf('Number of peaks: %i', size(TF(TF ~= 0), 2)), 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top')
        hold off
    end
    
    if (nargin == 2 && varargin{2} == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_no_outliers.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_no_outliers.png']);
    end
end