function [] = plot_raw_active_power(raw_eq_cell, units)
    % Objective: plot the original active power samples
    % Input: cell of the raw dataset data and string of the name of the table column 
    % Output: Figure with the raw unit data for each equipment

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    %sgtitle(join(['Raw ', strrep(string(units), '_', ' ')], ' '))

    counter = 1;
    for i = [1, 2, 3, 4, 7, 8] %1:size(raw_eq_cell, 2)
        eq_data = raw_eq_cell{i};

        date_mat = cell2mat(eq_data.timestamp);
        date_datetime = datetime(date_mat(:, 1:end - 3));

        % subplot(size(raw_eq_cell, 2) / 2, 2, i)
        %subplot(3, 2, counter)
        plot(date_datetime, eq_data.(units), '.')
        xlabel('Datestamp')  
        ylabel('Active Power [W]')
        title(sprintf('Equipment Active Power', i))
        labels_eq{counter} = sprintf('Equipment %d', i);
        counter = counter + 1;
        hold on;
    end
    legend(labels_eq)
end