function [curves, params_normal, pd] = get_params_normals(size_eq, TF_cell, counts_cell, edges_cell, bin_center_cell)
% Objective: calculate the curves that fit the histogram, per peak, with the allfitdist() and
% get the params of the normal function
% Inputs: TF_cell (one if is peak), counts_cell (count of each edge of hist)
% Outputs: curves (cell array), params_normal (cell array)

    for j = 1:size_eq
        peaks_index = find(TF_cell{j} == 1);
        mid_peaks_index = zeros(1, size(peaks_index, 2) - 1);
        for i = 1:size(peaks_index, 2) - 1
            mid_peaks_index(i) = round((peaks_index(i + 1) + peaks_index(i)) / 2);
        end
        
        counts = counts_cell{j};
        bin_center_var = bin_center_cell{j};
        edges_var = edges_cell{j};
        mid_peaks_index_interp = bin_center_var(mid_peaks_index);


        complete_edges = bin_center_var(1):bin_center_var(end);
        counts_interp = spline(bin_center_var, counts, complete_edges);
        
        % Debug
        plot(bin_center_var(1, 1:mid_peaks_index(1)), counts(1, 1:mid_peaks_index(1)), 'o')
        
        h = histogram(counts(1, 1:mid_peaks_index(1)), edges_var(1, 1:mid_peaks_index(1)));
        hold on
        pd = fitdist(counts(1, 1:mid_peaks_index(1))', 'Weibull');
        xgrid = bin_center_var(1, 1:mid_peaks_index(1));
        pdfEst = pdf(pd, xgrid);
        line(xgrid, pdfEst)

        %


        % figure,
        pd=[];
        for i = 1:size(peaks_index, 2)
            if (i == 1)
                % Multivariate Copula Analysis Toolbox (MvCAT) - allfitdist()
                curves(j, i) = {struct2table(allfitdist(counts(1, 1:mid_peaks_index(1))))};
                % curves(j, i) = {struct2table(allfitdist(counts_interp(1, 1:mid_peaks_index_interp(1))))};
                % pd(j, i) = {fitdist(counts_interp(1, 1:mid_peaks_index(1))', 'Normal')};
                
                % subplot(size(peaks_index, 2), 1, i);
                % histfit(counts_interp(1, 1:mid_peaks_index(1)))
            elseif (i == size(peaks_index, 2))
                curves(j, i) = {struct2table(allfitdist(counts(1, mid_peaks_index(end):end)) )};

                % curves(j, i) = {struct2table(allfitdist(counts_interp(1, mid_peaks_index_interp(end):end)) )};
                % pd(j, i) = {fitdist(counts_interp(1, mid_peaks_index(end):end)', 'Normal')};
                % pd(j, i) = {fitdist([zeros(1, mid_peaks_index(end) - 1), counts_interp(1, mid_peaks_index(end):end)]', 'Normal')};
                

                % subplot(size(peaks_index, 2), 1, i);
                % histfit(counts_interp(1, mid_peaks_index(end):end));
            else
                curves(j, i) = {struct2table(allfitdist(counts(1, mid_peaks_index(i - 1):mid_peaks_index(i))))};
                % curves(j, i) = {struct2table(allfitdist(counts_interp(1, mid_peaks_index_interp(i - 1):mid_peaks_index_interp(i))))};
                % pd(j, i) = {fitdist(counts_interp(1, mid_peaks_index(i - 1):mid_peaks_index(i))', 'Normal')};
                
                % subplot(size(peaks_index, 2), 1, i);
                % histfit(counts_interp(1, mid_peaks_index(i - 1):mid_peaks_index(i)));
            end
        end
    end 
    

    params_normal = cell(size(curves, 1), size(curves, 2));
    for i = 1:size(curves, 1)
        for j = 1:size(curves, 2)
            aux = curves(i, j);
            if (~isempty(aux{1}))
                normal_index = (string(aux{1}.DistName) == 'normal');
                params_normal(i, j) = aux{1}(normal_index,:).Params;
            end
        end
    end
end