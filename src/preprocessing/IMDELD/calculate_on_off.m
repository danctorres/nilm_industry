function [on_off_array] = calculate_on_off(data, threshold, selected_equipment_index)
    % Objective: Construct the on/off array with one flat power threshold
    % Input: data (table: timestamp, one active power column per equipment), threshold (same units as data), selected_equipment_index (for the plot titles)
    % Output: on_off_array (array with one if the equipment is in ON state for that sample, otherwise 0)

    on_off_array = double(table2array(data(:, 2:end)) > threshold);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]),
    for i = 1:size(on_off_array, 2)
        subplot(ceil(size(on_off_array, 2) / 2), 2, i)
        plot(on_off_array(:, i))
        xlabel('Sample Index', 'FontSize', 20);
        ylabel('State [OFF/ON]', 'FontSize', 20);
        title(sprintf('Equipment %i', selected_equipment_index(i)), 'FontSize', 20)
        xticklabels = get(gca, 'XTick');
        set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
        yticklabels = get(gca, 'YTick');
        set(gca, 'yticklabels', yticklabels, 'FontSize', 20);
    end
end
