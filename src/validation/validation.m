close all; clear; clc;

%% Read data
% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd(file_dir)

%% estimation UNN HIPE and IMDELD
estimations_unn_dir_hipe    = [erase(file_dir,'src\validation'), 'results\deep_learning\HIPE\1_week'];
est_unn_hipe_states         = read_results_csv(dir(join([estimations_unn_dir_hipe, '\states'])));
est_unn_hipe_fourier        = read_results_csv(dir(join([estimations_unn_dir_hipe, '\fourier'])));

for i = 1:size(est_unn_hipe_states, 2)
    est_unn_hipe_states_formatted{i} = est_unn_hipe_states{i}(:, 3:end);
    est_unn_hipe_fourier_formatted{i} = est_unn_hipe_fourier{i}(:, 3:end);
end

estimations_unn_dir_imdeld  = [erase(file_dir,'src\validation'), 'results\deep_learning\IMDELD'];
est_unn_imdeld_states       = read_results_csv(dir(join([estimations_unn_dir_imdeld, '\states'])));
est_unn_imdeld_fourier      = read_results_csv(dir(join([estimations_unn_dir_imdeld, '\fourier'])));

for i = 1:size(est_unn_imdeld_states, 2)
    est_unn_imdeld_states_formatted{i} = est_unn_imdeld_states{i}(:, 3:end);
    est_unn_imdeld_fourier_formatted{i} = est_unn_imdeld_fourier{i}(:, 3:end);
end

estimations_emupf_dir_hipe      = [erase(file_dir,'src\validation'), 'results\optimization\HIPE\1_week'];
est_emupf_hipe                  = read_results_csv(dir(estimations_emupf_dir_hipe));
est_emupf_hipe                  = est_emupf_hipe(1:8);

for i = 1:size(est_emupf_hipe, 2)
    est_emupf_hipe_formatted{i} = est_emupf_hipe{i}(:, 3:end);
end

estimations_unn_dir_imdeld      = [erase(file_dir,'src\validation'), 'results\optimization\IMDELD'];
est_emupf_imdeld                = read_results_csv(dir(estimations_unn_dir_imdeld));
est_emupf_imdeld                = est_emupf_imdeld(1);

for i = 1:size(est_emupf_imdeld, 2)
    est_emupf_imdeld_formatted{i} = est_emupf_imdeld{i}(:, 3:end);
end

true_dir_hipe               = [erase(file_dir,'src\validation'), 'data\processed\HIPE\1_week'];
true_eq_hipe                = read_results_csv(dir(join([true_dir_hipe, '\equipment_validation'])));

true_dir_imdeld             = [erase(file_dir,'src\validation'), 'data\processed\IMDELD\data_6_equipment'];
true_eq_imdeld              = readtable(join ([true_dir_imdeld, '\equipment_validation.csv']));

for i = 1:size(true_eq_hipe, 2)
    true_eq_hipe{i}.(1) = [];
end
true_eq_imdeld.(1) = [];

[error_emupf_hipe, error_emupf_imdeld] = calculate_all_errors_emupf(true_eq_hipe, est_emupf_hipe_formatted, true_eq_imdeld, est_emupf_imdeld_formatted);
[error_unn_hipe_states, error_unn_hipe_fourier, error_unn_imdeld_states, error_unn_imdeld_fourier] = calculate_all_errors_unn(true_eq_hipe, est_unn_hipe_states_formatted, est_unn_hipe_fourier_formatted, {true_eq_imdeld}, est_unn_imdeld_states_formatted, est_unn_imdeld_fourier_formatted);


%% Calculate error aggregate

% UNN
for i = 1:size(est_unn_hipe_states, 2)
    est_unn_hipe_states_agg{i}      = table(sum(table2array(est_unn_hipe_states_formatted{i}), 2));
    est_unn_hipe_fourier_agg{i}     = table(sum(table2array(est_unn_hipe_fourier_formatted{i}), 2));
    true_hipe_agg{i}            = est_unn_hipe_states{i}(:, 2);
end

for i = 1:size(est_unn_imdeld_states, 2)
    est_unn_imdeld_states_agg{i}    = table(sum(table2array(est_unn_imdeld_states_formatted{i}), 2));
    est_unn_imdeld_fourier_agg{i}   = table(sum(table2array(est_unn_imdeld_fourier_formatted{i}), 2));
    true_imdeld_agg{i}          = est_unn_imdeld_states{i}(:, 2);
end

% EMUPF
for i = 1:size(est_unn_hipe_states, 2)
    est_emupf_hipe_agg{i}           = table(sum(table2array(est_emupf_hipe_formatted{i}), 2));
end

for i = 1:size(est_unn_imdeld_states, 2)
    est_emupf_imdeld_agg{i}         = table(sum(table2array(est_emupf_imdeld_formatted{i}), 2));
end

[error_emupf_hipe_agg, error_emupf_imdeld_agg] = calculate_all_errors_emupf(true_hipe_agg, est_emupf_hipe_agg, true_imdeld_agg{1}, est_emupf_imdeld_agg);
[error_unn_hipe_states, error_unn_hipe_fourier, error_unn_imdeld_states, error_unn_imdeld_fourier] = calculate_all_errors_unn(true_hipe_agg, est_unn_hipe_states_agg, est_unn_hipe_fourier_agg, true_imdeld_agg, est_unn_imdeld_states_agg, est_unn_imdeld_fourier_agg);


%% Visualization

% Max, min and mean
[true_metrics_hipe_emupf, estimated_metrics_hipe_emupf]     = calculate_metrics(true_eq_hipe, est_emupf_hipe_formatted);
[true_metrics_imdeld_emupf, estimated_metrics_imdeld_emupf] = calculate_metrics({true_eq_imdeld}, est_emupf_imdeld_formatted);

[true_metrics_hipe_unn_states, estimated_metrics_hipe_unn_states]           = calculate_metrics(true_eq_hipe, est_unn_hipe_states_formatted);
[true_metrics_hipe_unn_fourier, estimated_metrics_hipe_unn_fourier]         = calculate_metrics(true_eq_hipe, est_unn_hipe_fourier_formatted);
[true_metrics_imdeld_unn_states, estimated_metrics_imdeld_unn_states]       = calculate_metrics({true_eq_imdeld}, est_unn_imdeld_states_formatted);
[true_metrics_imdeld_unn_fourier, estimated_metrics_imdeld_unn_fourier]     = calculate_metrics({true_eq_imdeld}, est_unn_imdeld_fourier_formatted);



%% Histogram
figure,
est_buff = est_unn_hipe_states{end};
for i = 3:size(est_buff, 2)
    subplot((size(est_buff, 2) - 1)/ 2, 2, i - 2)
    histogram(est_buff.(i))
end

figure,
est_buff = true_eq_hipe{end};
for i = 3:size(est_buff, 2)
    subplot((size(est_buff, 2) - 1)/ 2, 2, i - 2)
    histogram(est_buff.(i))
end

%%

% EMUPF IMDELD
close all;
figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
for i = 1:size(true_eq_imdeld, 2)
    subplot(size(true_eq_imdeld, 2) / 2, 2 , i)
    plot(true_eq_imdeld.(i), '.')
    hold on,
    plot(est_emupf_imdeld_formatted{1}.(i), '.')
    hold off,
    title(sprintf('Equipment %i', i))
    xlabel('Sample Index', 'FontSize', 15);
    ylabel("Active Power [W]", 'FontSize', 15);
    set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
    set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
    legend({'True'; 'Estimated'}, 'FontSize', 10);
end

% UNN states IMDELD
close all;
figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
for i = 1:size(true_eq_imdeld, 2)
    subplot(size(true_eq_imdeld, 2) / 2, 2 , i)
    plot(true_eq_imdeld.(i), '.')
    hold on,
    plot(est_unn_imdeld_states_formatted{1}.(i), '.')
    hold off,
    title(sprintf('Equipment %i', i))
    xlabel('Sample Index', 'FontSize', 15);
    ylabel("Active Power [W]", 'FontSize', 15);
    set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
    set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
    legend({'True'; 'Estimated'}, 'FontSize', 10);
end

% UNN fourier IMDELD
close all;
figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
for i = 1:size(true_eq_imdeld, 2)
    subplot(size(true_eq_imdeld, 2) / 2, 2 , i)
    plot(true_eq_imdeld.(i), '.')
    hold on,
    plot(est_unn_imdeld_fourier_formatted{1}.(i), '.')
    hold off,
    title(sprintf('Equipment %i', i))
    xlabel('Sample Index', 'FontSize', 15);
    ylabel("Active Power [W]", 'FontSize', 15);
    set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
    set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
    legend({'True'; 'Estimated'}, 'FontSize', 10);
end

% EMUPF HIPE
close all;
for j = 1:size(true_eq_hipe, 2)
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
    for i = 1:size(true_eq_hipe{j}, 2)
        subplot_size = floor(size(true_eq_hipe{j}, 2));
        if mod(subplot_size, 2) ~= 0
            subplot_size = subplot_size + 1;
        end
        largest_divisor = find_largest_divisor(subplot_size);
        subplot(subplot_size / largest_divisor, largest_divisor, i)
        plot(1:1:size(true_eq_hipe{j}.(i), 1), true_eq_hipe{j}.(i), '.')
        hold on,
        plot(1:1:size(true_eq_hipe{j}.(i), 1), est_emupf_hipe_formatted{j}.(i), '.')
        hold off,
        title(sprintf('Equipment %i', i))
        xlabel('Sample Index', 'FontSize', 15);
        ylabel("Active Power [W]", 'FontSize', 15);
        set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
        set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
        legend({'True'; 'Estimated'}, 'FontSize', 10);
    end
end

% UNN state HIPE
close all;
for j = 1:size(true_eq_hipe, 2)
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
    for i = 1:size(true_eq_hipe{j}, 2)
        subplot_size = floor(size(true_eq_hipe{j}, 2));
        if mod(subplot_size, 2) ~= 0
            subplot_size = subplot_size + 1;
        end
        largest_divisor = find_largest_divisor(subplot_size);
        subplot(subplot_size / largest_divisor, largest_divisor, i)
        plot(1:1:size(true_eq_hipe{j}.(i), 1),  true_eq_hipe{j}.(i), '.')
        ymin = min(min(true_eq_hipe{j}.(i)), min(est_unn_hipe_states_formatted{j}.(i)));
        ymax = max(max(true_eq_hipe{j}.(i)), max(est_unn_hipe_states_formatted{j}.(i)));
        hold on,
        plot(1:1:size(true_eq_hipe{j}.(i), 1), est_unn_hipe_states_formatted{j}.(i), '.')
        xlabel('Sample Index', 'FontSize', 15);
        ylabel("Active Power [W]", 'FontSize', 15);
        
        set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
        set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
        legend({'True'; 'Estimated'}, 'FontSize', 10);
        title(sprintf('Equipment %i', i))
    end
end

% UNN fourier HIPE
close all;
for j = 1:size(true_eq_hipe, 2)
    figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
    for i = 1:size(true_eq_hipe{j}, 2)
        subplot_size = floor(size(true_eq_hipe{j}, 2));
        if mod(subplot_size, 2) ~= 0
            subplot_size = subplot_size + 1;
        end
        largest_divisor = find_largest_divisor(subplot_size);
        subplot(subplot_size / largest_divisor, largest_divisor, i)
        plot(1:1:size(true_eq_hipe{j}.(i), 1), true_eq_hipe{j}.(i), '.')
        hold on,
        plot(1:1:size(true_eq_hipe{j}.(i), 1), est_unn_hipe_fourier_formatted{j}.(i), '.')
        title(sprintf('Equipment %i', i))
        xlabel('Sample Index', 'FontSize', 15);
        ylabel("Active Power [W]", 'FontSize', 15);
        set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto', 'FontSize', 15);
        set(gca, 'YTickMode', 'auto', 'YTickLabelMode', 'auto', 'FontSize', 15);
        legend({'True'; 'Estimated'}, 'FontSize', 10);
    end
end
