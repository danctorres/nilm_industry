function [] = save_final_data(aggregate, on_off, equipment_active_pow, selected_equipment_index, ratio, out_dir)
    % Objective: divide data into training and validation by applying adaptive binning to the aggregate active power, and save it
    % Input: aggregate (table), on_off (array, one column per selected equipment), equipment_active_pow (table),
    %        selected_equipment_index, ratio (training share), out_dir (data/processed/IMDELD/data_<N>_equipment)
    % Output: aggregate, on_off, equipment and their _training / _validation csv files in out_dir

    [training_index, validation_index] = split_train_validation(aggregate.active_power, ratio);

    state_names = {'State DPCI', 'State DPCII', 'State EFI', 'State EFII', 'State MI', 'State MII', 'State PI', 'State PII'};
    on_off = array2table(on_off, 'VariableNames', state_names(selected_equipment_index));
    on_off = addvars(on_off, aggregate.timestamp, 'Before', 1, 'NewVariableNames', 'Timestamp');

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle('Adaptive binning')
    subplot(3, 1, 1)
    plot(aggregate.active_power, '.');
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Original data')
    subplot(3, 1, 2)
    plot(aggregate.active_power(training_index), '.');
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Training data')
    subplot(3, 1, 3)
    plot(aggregate.active_power(validation_index), '.');
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Validation data')

    writetable(aggregate(:, 1:2), fullfile(out_dir, 'aggregate.csv'));
    writetable(on_off, fullfile(out_dir, 'on_off.csv'));
    writetable(equipment_active_pow, fullfile(out_dir, 'equipment.csv'));

    writetable(aggregate(training_index, :), fullfile(out_dir, 'aggregate_training.csv'));
    writetable(aggregate(validation_index, :), fullfile(out_dir, 'aggregate_validation.csv'));
    writetable(on_off(training_index, :), fullfile(out_dir, 'on_off_training.csv'));
    writetable(on_off(validation_index, :), fullfile(out_dir, 'on_off_validation.csv'));
    writetable(equipment_active_pow(training_index, :), fullfile(out_dir, 'equipment_training.csv'));
    writetable(equipment_active_pow(validation_index, :), fullfile(out_dir, 'equipment_validation.csv'));
end
