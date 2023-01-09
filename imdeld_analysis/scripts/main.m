%% %%%%%%%%%%%%%% NILM dissertation dataset analysis code %%%%%%%%%%%%%% %%
% Daniel Torres
% 09/12/2022



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% CORE CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%% %%
close all; clear; clc;

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));
clearvars file_ext file_name file_information

% Read the data from the equipment csv files
equip_data = read_equipment_csv(); % read dataset equipment csv

% Identify common timestamps among equipment
common_timestamps = find_common_timestamps(equip_data);

% Filter timestamps to obtain only those corresponding to days with relevant data
useful_common_timestamps = find_useful_timestamps(common_timestamps);

% Construct a table containing the timestamps and corresponding active power values for each piece of equipment
date_active_power = construct_date_power_table(equip_data, useful_common_timestamps);

% Interpolate the active power values to obtain a complete set of data the choosen days
equipment_formated = interpolate_equipment_data(date_active_power, false);

% Read and format data from 'pelletizer-subcircuit.csv' and 'millingmachine-subcircuit.csv'
lvdb2_table = read_lvdb2_csv(false);
lvdb3_table = read_lvdb3_csv(false);

% Compute the total power consumption  by summing LVDB2 and LVDB3
aggregate_table = calculate_aggregate(false, lvdb2_table, lvdb3_table);

[counts_cell, edges_cell, bin_center_cell, TF_cell] = histogram_without_outliers(equipment_formated, false);
[curves, params_normal, ~] = get_params_normals(size(equipment_formated, 2) - 1, TF_cell, counts_cell, edges_cell, bin_center_cell);

%% %%%%%%%%%%%%%%%%%%%%%%%%%% ADDITIONAL CODE %%%%%%%%%%%%%%%%%%%%%%%%%% %%
[number_samples, unique_samples, not_unique_samples, nan_samples, array_start, array_end] = number_non_unique(equip_data);
[day1, day2, interval, number_missing_samples, mean_missing_samples, median_missing_samples] = common_timestamps_metrics(common_timestamps);
average_power_day = calculate_average_power_day(date_active_power);
histogram_equipment_original(equip_data, false);
plot_active_power_per_day(date_active_power, false);
plot_power_selected_days(equipment_formated, false);
histogram_equipment_formated(equipment_formated, false);

statistics_result_cell = statistical_diff_lvdb_aggregate(equipment_formated, lvdb2_table, lvdb3_table, aggregate_table, false);

% table_2_json(); % Convert a table and save it has a json


%% %%%%%%%%%%%%%%%% Currently in development
% Plot gaussians
 for j = 1:size(equipment_formated, 2) - 1
        peaks_index = find(TF_cell{j} == 1);
        mid_peaks_index = zeros(1, size(peaks_index, 2) - 1);
        for i = 1:size(peaks_index, 2) - 1
            mid_peaks_index(i) = round((peaks_index(i + 1) + peaks_index(i)) / 2);
        end
        
        counts = counts_cell{j};
        for i = 1:size(peaks_index, 2)
            if (i == 1)
                % Multivariate Copula Analysis Toolbox (MvCAT) - allfitdist()
                counts_group(j, i) = {counts(1, 1:mid_peaks_index(1))};
            elseif (i == size(peaks_index, 2))
                counts_group(j, i) = {counts(1, mid_peaks_index(end):end)};
            else
                counts_group(j, i) = {counts(1, mid_peaks_index(i - 1):mid_peaks_index(i))};
            end
        end
    end 


for i = 1:size(params_normal, 1)
    figure,
    sgtitle(sprintf('Equipment % i', i));
    for j = 1:size(params_normal, 2)
        aux = cell2mat(params_normal(i, j));
        if (~isempty(aux))
            mu = aux(1, 1);
            sigma = aux(1, 2);
            x = -15*mu:15*mu;
            y = normpdf(x,mu,sigma);
            subplot(size(params_normal, 2), 1, j)
            plot(x, y)
            title(sprintf('State %i', j - 1));
        end
    end
end





% Remove outliers
% figure;
% for i = 1:size(equipment_formated, 2) - 1
%     x_clean = rmoutliers(table2array(equipment_formated(:, i + 1)), 'mean', 'ThresholdFactor', 3);
%     subplot((size(equipment_formated, 2) - 1) / 2, 2, i);
%     plot(x_clean)
% end

% read csv
file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd([erase(file_information.Filename, ['\scripts\', file_name, file_ext]), '\results\data\hdbscan']);

file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end);



equip_data = cell(1, size(file_list, 2));
for i = 1:size(file_list, 2)
    equip_data{i} = readtable(string(file_list(i)));
end


ht_1 = readtable("histogram_eq7.csv");
lt_1 = readtable("labels_eq7.csv");
edges = [ht_1.LeftEdges; ht_1.RightEdges(end)]';
counts = ht_1.FrequencyCount';
h = histogram('BinEdges', edges,'BinCounts', counts);
hold on
scatter(ht_1.x_BinCenter, counts, 20, lt_1.x_Cluster);

for i = 1:size(counts, 2)
    set(bars(i), 'FaceColor', colors{i,1});
end

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));
%%%%%%%%%%%%%%%%%%%% %% Linting and Indentation tool %% %%%%%%%%%%%%%%%%%%%%
close all;  clc;

file_information = matlab.desktop.editor.getActive;
[~, file_name, file_ext] = fileparts(file_information.Filename);
cd(erase(file_information.Filename, [file_name, file_ext]));

file_list = dir;
file_list = {file_list.name};
file_list = file_list(3:end); % remove . and ..

checkcode(file_list(endsWith(file_list, 'm')))

% Indentation tool
% git clone github.com/davidvarga/MBeautifier into the same path level that dissertation_nilm
mbeautify_path = [erase(file_information.Filename, ['dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
cd(mbeautify_path);
source_folder = ([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\']);

% mbeautify_path = [erase(file_information.Filename, ['\dissertation_nilm\imdeld_analysis\scripts\', file_name, file_ext]), '\MBeautifier\'];
% cd(mbeautify_path);
% files_names = file_list(endsWith(file_list, 'm'));
% for i = 1:size(files_names, 2)
%     MBeautify.formatFile([erase(mbeautify_path, '\MBeautifier\'), '\dissertation_nilm\imdeld_analysis\scripts\', files_names{i}]);
% end
 