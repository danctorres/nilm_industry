function [aggregate_training, aggregate_validation, on_off_training, on_off_validation, equipment_validation] = save_final_data(aggregate, on_off, equipment_active_pow, percentage_train, save)
    % Objective: divide data into training and validation
    % Input: aggregate_table and on_off_array
    % Output: aggregate_training, aggregate_validation, on_off_training, on_off_validation

    % Divide into 70% training, 30% testing and equipment power consumption for validation
    size_training = round(size(aggregate, 1) * percentage_train);
    
    aggregate_training      = aggregate(1:size_training, :);
    aggregate_validation    = aggregate(size_training:end, :);
    on_off_training         = on_off(1:size_training, :);
    on_off_validation       = on_off(size_training:end, :);

    equipment_validation    = equipment_active_pow(size_training:end, :);

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