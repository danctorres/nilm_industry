 figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
plot(table2array(aggregate_formated_table(:, "active_power")), '.')
%title("Aggregate Active Power", 'FontSize', 20);
xlabel('Sample Index', 'FontSize', 20);
ylabel("Active Power [W]", 'FontSize', 20);
xticklabels = get(gca, 'XTick');
set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
yticklabels = get(gca, 'YTick');
set(gca, 'yticklabels', yticklabels, 'FontSize', 20);


file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
aggregate_training = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\aggregate_training.csv');
aggregate_validation = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\aggregate_validation.csv');

% equipment_training = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\equipment_training.csv');
equipment_validation = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\equipment_validation.csv');

on_off_training = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\on_off_training.csv');
on_off_validation = readmatrix('\\wsl.localhost\ubuntu\home\dtorres\dissertation_nilm\data\processed\IMDELD\data_6_equipment\on_off_validation.csv');

figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
plot(aggregate_training(:, 2), '.')
title('Aggregate Active Power', 'FontSize', 20);
xlabel('Sample Index', 'FontSize', 20);
ylabel('Active Power [W]', 'FontSize', 20);

figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
plot(aggregate_validation(:, 2), '.')
title('Aggregate Active Power', 'FontSize', 20);
xlabel('Sample Index', 'FontSize', 20);
ylabel('Active Power [W]', 'FontSize', 20);


figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
sgtitle('Equipment States', 'FontSize', 20);
eq_index = [1, 2, 3, 4, 7, 8];
for i = 1:6
    subplot(3, 2, i)
    plot(on_off_training(:, i + 1))
    title(sprintf('Equipment %d', eq_index(i)), 'FontSize', 20);
    xlabel('Sample Index', 'FontSize', 20);
    ylabel('State [ON/OFF]', 'FontSize', 20);
end

figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
sgtitle('Equipment States', 'FontSize', 20);
eq_index = [1, 2, 3, 4, 7, 8];
for i = 1:6
    subplot(3, 2, i)
    plot(on_off_validation(:, i + 1))
    title(sprintf('Equipment %d', eq_index(i)), 'FontSize', 20);
    xlabel('Sample Index', 'FontSize', 20);
    ylabel('State [ON/OFF]', 'FontSize', 20);
end

figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
plot(equipment_validation(:, 2:end), '.')
title('Equipment Active Power', 'FontSize', 20);
xlabel('Sample Index', 'FontSize', 20);
ylabel('Active Power [W]', 'FontSize', 20);
legend(['Equipment 1'; 'Equipment 2'; 'Equipment 3'; 'Equipment 4'; 'Equipment 7'; 'Equipment 8'], 'FontSize', 20);


figure,
subplot(3, 1, 1)
plot(aggregate_validation(:, 2))
subplot(3, 1, 2)
plot(on_off_training(:, 2:end))
subplot(3, 1, 3)
plot(equipment_validation(:, 2:end))


figure('units', 'normalized', 'outerposition', [0, 0, 1, 1]);
x = [-3:0.01:3];
plot(x, max(0, x), 'LineWidth', 2)
%title("Aggregate Active Power", 'FontSize', 20);
xlabel('x', 'FontSize', 20);
ylabel("f(x)", 'FontSize', 20);
xticklabels = get(gca, 'XTick');
set(gca, 'xticklabels', xticklabels, 'FontSize', 20);
yticklabels = get(gca, 'YTick');
set(gca, 'yticklabels', yticklabels, 'FontSize', 20);

