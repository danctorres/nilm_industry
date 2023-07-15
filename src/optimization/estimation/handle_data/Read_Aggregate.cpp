//
// Created by danctorres on 3/5/23.
//

#include "Read_Aggregate.h"


Read_Aggregate::Read_Aggregate(const std::string& name_file) : Read(name_file) {
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        timestamp.push_back(data[i][0]);
        active_power.push_back(std::stof(data[i][1]));
        // reactive_power.push_back(std::stof(data[i][2]));
        // apparent_power.push_back(std::stof(data[i][3]));
        // current.push_back(std::stof(data[i][4]));
        // voltage.push_back(std::stof(data[i][5]));
        // power_factor.push_back(std::stof(data[i][6]));
    }
}

std::variant<std::vector<std::string>, std::vector<float>> Read_Aggregate::get_parameters(const std::string& name_parameter) const {
    if (name_parameter == "Timestamp") {
        return timestamp;
    }
    else if (name_parameter == "Active power") {
        return active_power;
    }
    // else if (name_parameter == "Reactive power") {
    //     return reactive_power;
    // }
    // else if (name_parameter == "Apparent power") {
    //     return apparent_power;
    // }
    // else if (name_parameter == "Current") {
    //     return current;
    // }
    // else if (name_parameter == "Voltage") {
    //     return voltage;
    // }
    // else if (name_parameter == "Power factor") {
    //     return power_factor;
    // }
    else {
        std::cerr << "The parameter " << name_parameter << " name not define, use valid name!" << std::endl;
        throw;
    }
}

std::variant<std::string, float> Read_Aggregate::get_one_parameter(const std::string &name_parameter, const int sample) const {
    if (name_parameter == "Timestamp") {
        return timestamp[sample];
    }
    else if (name_parameter == "Active power") {
        return active_power[sample];
    }
    // else if (name_parameter == "Reactive power") {
    //     return reactive_power[sample];
    // }
    // else if (name_parameter == "Apparent power") {
    //     return apparent_power[sample];
    // }
    // else if (name_parameter == "Current") {
    //     return current[sample];
    // }
    // else if (name_parameter == "Voltage") {
    //     return voltage[sample];
    // }
    // else if (name_parameter == "Power factor") {
    //     return power_factor[sample];
    // }
    else {
        std::cerr << "The parameter " << name_parameter << " name not define, use valid name!" << std::endl;
        throw;
    }
}

int Read_Aggregate::size() {
    return timestamp.size();
}
