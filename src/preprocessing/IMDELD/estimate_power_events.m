function [power_events_cell] = estimate_power_events(aggregate_table, on_off_array)
    % Objective: estimate the power of each equipment at the events
    % Input: aggregate_table and on_off_arrayon_off_array
    % Output: power_events_cell

    aggregate_array = table2array(aggregate_table(:, 2));
    events_index = false(size(on_off_array, 1), size(on_off_array, 2));
    % aggregate_array_clean = rmoutliers(aggregate_array(:, 1), 'mean', 'ThresholdFactor', 3);
    figure('units', 'normalized', 'outerposition', [0 0 1 1]),
    sgtitle('Estimated active power equipment consumption based on events')
    for i = 1:size(on_off_array, 2)
        events_index(:, i) = logical([diff(on_off_array(:, i)) ~= 0; 0]);
        power_events_cell(:, i) = {abs(diff(aggregate_array(events_index(:, i))))};
        subplot(size(on_off_array, 2) / 2, 2, i)
        plot(power_events_cell{i}, '.');

        % power_events_cell_clean = rmoutliers(cell2mat(power_events_cell(:, i)), 'mean', 'ThresholdFactor', 3);
        % histogram(power_events_cell_clean, 100)
        % histogram(power_events_cell{i}, 100);

        ylabel('Active Power [W]')
        title(sprintf('Equipment %i', i))
        hold on
        plot(1:size(power_events_cell{i}, 1), polyval( polyfit(1:size(power_events_cell{i}, 1), power_events_cell{i}, 1), 1:size(power_events_cell{i}, 1)), 'r--', 'LineWidth', 2)
        hold off
    end

    figure('units', 'normalized', 'outerposition', [0 0 1 1]),
    for i = 1:size(on_off_array, 2)
        events_index(:, i) = logical([diff(on_off_array(:, i)) ~= 0; 0]);
        power_events_cell(:, i) = {abs(diff(aggregate_array(events_index(:, i))))};
        subplot(size(on_off_array, 2) / 2, 2, i)
        histogram(power_events_cell{i});
    end

end