function [] = plot_aggregate_vs_equipment(aggregate_formated_table, active_power_formated)
    % Objective: Plot aggregate features vs equipment active power
    % Inputs: aggregate features vs equipment active power

    for i = 2:size(aggregate_formated_table, 2)
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
        sgtitle(sprintf('Aggregate %s vs equipment active power', strrep(aggregate_formated_table.Properties.VariableNames{i}, '_', ' ')))
        for j = 2:size(active_power_formated, 2)
            subplot((size(active_power_formated, 2) - 1)/ 2, 2, j - 1)
            plot(active_power_formated.(j), aggregate_formated_table.(i), '.')

            xlabel(sprintf('Aggregate %s', strrep(aggregate_formated_table.Properties.VariableNames{i}, '_', ' ')))
            ylabel('Equipment active power [W]')
            title(sprintf('Equipment %i', j - 1))
        end
    end
end