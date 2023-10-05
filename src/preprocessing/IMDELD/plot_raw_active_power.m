function [] = plot_raw_active_power(raw_eq_cell, units)
    % Objective: plot the original active power samples
    % Input: cell of the raw dataset data and string of the name of the table column
    % Output: Figure with the raw unit data for each equipment

%     figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
%     counter = 1;
%     for i = [1, 2, 3, 4, 7, 8] %1:size(raw_eq_cell, 2)
%         eq_data = raw_eq_cell{i};
%
%         date_mat = cell2mat(eq_data.timestamp);
%         date_datetime = datetime(date_mat(:, 1:end - 3));
%
%         plot(date_datetime, eq_data.(units), '.');
%
%         labels_eq{counter} = sprintf('Equipment %d', i);
%         counter = counter + 1;
%         hold on;
%     end
%     hold off;
%     % title(sprintf('Equipment Active Power', i), 'FontSize', 20);
%     legend(labels_eq, 'FontSize', 20);
%     xticklabels = get(gca, 'xticklabels');
%     set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
%     yticklabels = get(gca, 'YTick');
%     set(gca, 'yticklabels', yticklabels, 'FontSize', 20);
%     xlabel('Datestamp', 'FontSize', 20);
%     ylabel('Active Power [W]', 'FontSize', 20);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    counter = 1;
    for i = [1, 2, 3, 4, 7, 8] %1:size(raw_eq_cell, 2)
        eq_data = raw_eq_cell{i};

        date_mat = cell2mat(eq_data.timestamp);
        date_datetime = datetime(date_mat(:, 1:end - 3));

        %subplot(size(raw_eq_cell, 2) / 2, 2, i)
        subplot(3, 2, counter)
        plot(date_datetime, eq_data.(units), '.');

        % aux = eq_data.(units);
        % histogram(aux(aux > 0));
        % ylabel('Number of samples', 'FontSize', 15);
        % xlabel('Active Power [W]', 'FontSize', 15);

        xlabel('Datestamp', 'FontSize', 15);
        ylabel('Active Power [W]', 'FontSize', 15);
        xticklabels = get(gca, 'xticklabels');
        set(gca, 'xticklabels', xticklabels, 'FontSize', 15);
        yticklabels = get(gca, 'YTick');
        set(gca, 'yticklabels', yticklabels, 'FontSize', 15);
        title(sprintf('Equipment %d', i), 'FontSize', 20);
        counter = counter + 1;
    end
end
