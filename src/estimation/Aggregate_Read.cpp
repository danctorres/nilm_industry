//
// Created by dtorres on 3/5/23.
//

#include "Aggregate_Read.h"
#include <iostream>
#include <string>
#include <vector>

void Aggregate_Read::set_parameters(){
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        timestamp.push_back(std::stoi(data[i][0]));
        active_power.push_back(std::stoi(data[i][1]));
        reactive_power.push_back(std::stoi(data[i][2]));
        apparent_power.push_back(std::stoi(data[i][3]));
        current.push_back(std::stoi(data[i][4]));
        voltage.push_back(std::stoi(data[i][5]));
        power_factor.push_back(std::stoi(data[i][6]));
    }
}

std::vector<uint_fast32_t> Aggregate_Read::get_parameter(const std::string name_parameter) const {
    if (name_parameter == "Timestamp"){
        return timestamp;
    }
    if (name_parameter == "Active Power"){
        return active_power;
    }
    if (name_parameter == "Reactive Power"){
        return reactive_power;
    }
    if (name_parameter == "Apparent Power"){
        return apparent_power;
    }
    if (name_parameter == "Current"){
        return current;
    }
    if (name_parameter == "Voltage"){
        return voltage;
    }
    if (name_parameter == "Power Factor"){
        return power_factor;
    }
    else{
        std::cerr << "Parameter name not define, use valida name!" << std::endl;
        throw;
    }
}

