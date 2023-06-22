close all; clear; clc;

% Set path
file_information = matlab.desktop.editor.getActive;
[file_dir, ~, ~] = fileparts(file_information.Filename);
cd([erase(file_dir, 'HIPE'), 'IMDELD']);

equip_data = read_equipment_csv('HIPE');

cd(file_dir);
agg_data = read_aggregate('HIPE');
clearvars file_dir file_information



numRows = ceil(sqrt(size(equip_data, 2)));
numCols = ceil(size(equip_data, 2) / 4);


figure,
clear equipment_tab;
for i = 1 : size(equip_data, 2)
   equipment_tab{i} = equip_data{i}(:, {'SensorDateTime', 'P_kW'});
   columnData = equipment_tab{i}.P_kW;
   subplot(numRows, numCols, i);
   plot(columnData);
end

equipment_processed_tab = {};
figure,
for i = 1 : size(equip_data, 2)
    myTable1 = equipment_tab{i};
    myTable1.SensorDateTime = cellfun(@(x) x(1, 1:22), myTable1.SensorDateTime, 'UniformOutput', false);
    myTable1.SensorDateTime = strrep(myTable1.SensorDateTime, '+', '.');
    myTable1.SensorDateTime = datetime(myTable1.SensorDateTime, 'InputFormat',"yyyy-MM-dd'T'HH:mm:ss.SS");
    
    stopIndex = find(diff(myTable1.SensorDateTime) <= 0, 1);
    if stopIndex > 0
        myTable1(stopIndex : end, :) = [];
    end
    clear stopIndex;

    TT1 = timetable(myTable1.SensorDateTime, myTable1.P_kW);
    newTimeVector = myTable1.SensorDateTime(1):seconds(1):myTable1.SensorDateTime(end);
    newTable = retime(TT1, newTimeVector, 'linear');
    clear newTimeVector;

    equipment_processed_tab{i} = newTable;
    subplot(numRows, numCols, i);
    plot(newTable.Var1)
    clear newTable;
end

aux1 = equipment_processed_tab{1};
synchronizedTable = synchronize(equipment_processed_tab{:},'union','linear');


ON_OFF = timetable2table(synchronizedTable);
ON_OFF = table2array(ON_OFF(:, 2:end));
ON_OFF(ON_OFF > 0) = 1;
ON_OFF(ON_OFF < 0) = 0;

figure,
for i = 1 : size(ON_OFF, 2)
    subplot(numRows, numCols, i);
    plot(ON_OFF(:, i));
end

