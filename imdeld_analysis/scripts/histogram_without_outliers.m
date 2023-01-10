function [output_counts_cell, output_edges_cell, output_bin_center, output_TF_cell] = histogram_without_outliers(varargin)
    % Objective: Create histograms of all the equipment active power samples for selected days
    % Input: equipment_formated, minimum_prominence (value for islocalmax
    % function), true or false for removing outliers, save or not image
    % Output: histogram images

    equipment_formated = varargin{1};
    output_counts_cell      = cell(1, size(equipment_formated, 2) - 1);
    output_edges_cell       = cell(1, size(equipment_formated, 2) - 1);
    output_bin_center       = cell(1, size(equipment_formated, 2) - 1);
    output_TF_cell          = cell(1, size(equipment_formated, 2) - 1);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    for i = 1:size(equipment_formated, 2) - 1
        subplot((size(equipment_formated, 2) - 1) / 2, 2, i)
        data = table2array(equipment_formated(:, i + 1));
        if varargin{3} == true
            x_clean = rmoutliers( data(data >= 0), 'mean', 'ThresholdFactor', 3);
        else
            x_clean = data;
        end

        [counts, edges] = histcounts(x_clean);
        histHandle      = histogram('BinEdges', edges, 'BinCounts', counts);
        bin_center      = histHandle.BinEdges + histHandle.BinWidth/2;
        bin_center      = bin_center(1:end - 1);
        hold on

        % minimum_prominence = varargin{2}
        [TF, ~] = islocalmax([0, counts], 'MinProminence', varargin{2});

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
    
    if (nargin == 3 && varargin{3} == true)
        file_information = matlab.desktop.editor.getActive;
        [~, file_name, file_ext] = fileparts(file_information.Filename);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_no_outliers.fig']);
        saveas(gcf, [erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\images\histogram_equipment_no_outliers.png']);
    end
end