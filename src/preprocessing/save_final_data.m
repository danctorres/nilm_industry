function [aggregate_training, aggregate_validation, on_off_training, on_off_validation, equipment_validation] = save_final_data(aggregate, on_off, equipment_active_pow, percentage_train, save)
    % Objective: divide data into training and validation, by appling adaptive binning
    % Input: aggregate_table and on_off_array
    % Output: aggregate_training, aggregate_validation, oregaten_off_training, on_off_validation

    % Divide into 70% training, 30% testing and equipment power consumption for validation

    % Divide aggregate active power into bins
    mean_aggregate  = mean(aggregate.(2));
    std_aggregate   = std(aggregate.(2));
    bin_edges       = mean_aggregate + [-3 * std_aggregate, -2 * std_aggregate, -1 * std_aggregate, 0, 1 * std_aggregate, 2 * std_aggregate, 3 * std_aggregate];
    [~, ~, bin]     = histcounts(aggregate.(2), bin_edges);
    
    unique_bins         = unique(bin);
    n_samples_bin       = 1000 * percentage_train;
    % for i = 1:size(unique_bins, 1)
    %    n_samples_bin   = min(n_samples_bin, round(size(aggregate.(2)(bin == unique_bins(i)), 1) * percentage_train));      % min between the smallest bin size * percentage_train
    % end

    training_index      = [];
    validation_index    = [];
    for i = 1:size(unique_bins, 1)
        bin_samples             = find(bin == unique_bins(i));
        bin_index_training      = randsample(bin_samples, n_samples_bin);
        bin_index_validation    = randsample(setdiff(bin_samples, bin_index_training), round(n_samples_bin * (1 - percentage_train)));
        training_index          = [training_index; bin_index_training];
        validation_index        = [validation_index; bin_index_validation]; % setdiff(1:size(aggregate.(2)), training_index);
    end

    training_index = sort(training_index);
    validation_index = sort(validation_index);

    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
    sgtitle('Adaptive binning')
    subplot(3, 1, 1)
    plot(aggregate.(2));
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Original data')
    subplot(3, 1, 2)
    plot(aggregate.(2)(training_index));
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Training data')
    subplot(3, 1, 3)
    plot(aggregate.(2)(validation_index));
    xlabel('Samples')
    ylabel('Active Power [W]')
    title('Validation data')

    % Convert to posix time format
    aggregate.timestamp     = posixtime(table2array(aggregate(:, 1)));

    % Split into training and validation data
    aggregate_training      = aggregate(training_index, :);
    aggregate_validation    = aggregate(validation_index, :);
    on_off_training         = on_off(training_index, :);
    on_off_validation       = on_off(validation_index, :);

    equipment_validation    = equipment_active_pow(validation_index, :);

    if save == true
        file_information    = matlab.desktop.editor.getActive;
        [~, file_name, ~] = fileparts(file_information.Filename);
        writetable(aggregate_training, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\processed\aggregate_training.csv'], '\'));
        writetable(aggregate_validation, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\processed\aggregate_validation.csv'], '\'));
        writematrix(on_off_training, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\processed\on_off_training.csv'], '\'))
        writematrix(on_off_validation, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\processed\on_off_validation.csv'], '\'))
        writetable(equipment_validation, join([erase(file_information.Filename,  join(['\src\preprocessing\', file_name, '.m'])), '\data\processed\equipment_validation.csv'], '\'));
    end
end