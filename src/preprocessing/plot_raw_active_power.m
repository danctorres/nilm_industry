function [] = plot_raw_active_power(raw_eq_cell, units)
    % Objective: plot the original active power samples
    % Input: cell of the raw dataset data and string of the name of the table column 
    % Output: Figure with the raw unit data for each equipment

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    sgtitle(join(['Raw ', strrep(string(units), '_', ' ')], ' '))
    for i = 1:size(raw_eq_cell, 2)
        eq_data = raw_eq_cell{i};
        subplot(size(raw_eq_cell, 2) / 2, 2, i)
        plot(eq_data.(units))
        xlabel('Samples')  
        ylabel('Active Power [W]')
        title(sprintf('Equipment %i', i))
    end
end