function [corr] = calculate_corr_aggregate_eq(aggregate, eq_table)
    % Objectives: Calculate the correlation coefficients and plot a heatmap
    % between an aggregate features and the respective equipment valus
    corr = zeros(1 - size(aggregate, 2), 1 - size(aggregate, 2));
    for j = 2:size(aggregate, 2)
        for i = 2:size(eq_table, 2)
            c = corrcoef(aggregate.(j)(:), eq_table.(i)(:));
            corr(j - 1, i - 1) = c(1, 2);
        end
    end
    ylabel = aggregate.Properties.VariableNames;
    xlabel = eq_table.Properties.VariableNames;
    h = heatmap(strrep(xlabel(2:end), '_', ' '), strrep(ylabel(2:end), '_', ' '), corr);
    h.Title = 'Correlation';
    h.XLabel = 'Equipment';
    h.YLabel = 'Aggregate';
end