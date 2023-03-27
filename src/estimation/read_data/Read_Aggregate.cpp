//
// Created by dtorres on 3/5/23.
//
#include <iostream>
#include <string>
#include <vector>
#include "Read_Aggregate.h"

Read_Aggregate::Read_Aggregate(const std::string& name_file) : Read(name_file){
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        timestamp.push_back(std::stof(data[i][0]));
        active_power.push_back(std::stof(data[i][1]));
        reactive_power.push_back(std::stof(data[i][2]));
        apparent_power.push_back(std::stof(data[i][3]));
        current.push_back(std::stof(data[i][4]));
        voltage.push_back(std::stof(data[i][5]));
        power_factor.push_back(std::stof(data[i][6]));
    }
}

std::vector<float> Read_Aggregate::get_parameter(const std::string &name_parameter) const {
    if (name_parameter == "Timestamp"){
        return timestamp;
    }
    if (name_parameter == "Active power"){
        return active_power;
    }
    if (name_parameter == "Reactive power"){
        return reactive_power;
    }
    if (name_parameter == "Apparent power"){
        return apparent_power;
    }
    if (name_parameter == "Current"){
        return current;
    }
    if (name_parameter == "Voltage"){
        return voltage;
    }
    if (name_parameter == "Power factor"){
        return power_factor;
    }
    else{
        std::cerr << "Parameter name not define, use valida name!" << std::endl;
        throw;
    }
}

std::vector<std::vector<float>> Read_Aggregate::get_all_parameters() const {
    std::vector<std::vector<float>> data;
    data.push_back(timestamp);
    data.push_back(apparent_power);
    data.push_back(reactive_power);
    data.push_back(apparent_power);
    data.push_back(current);
    data.push_back(voltage);
    data.push_back(power_factor);
    return data;
}