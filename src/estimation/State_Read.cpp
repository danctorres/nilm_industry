//
// Created by danie on 3/7/2023.
//

#include "State_Read.h"
#include <iostream>
#include <string>
#include <vector>

void State_Read::set_parameters(){
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size(); i++){
        for (int j = 0; j < data[i].size(); j++) {
            state_0.push_back(std::stoi(data[i][0]));
            state_1.push_back(std::stoi(data[i][1]));
            state_2.push_back(std::stoi(data[i][2]));
            state_3.push_back(std::stoi(data[i][3]));
            state_4.push_back(std::stoi(data[i][4]));
            state_5.push_back(std::stoi(data[i][5]));
        }
    }
}

std::vector<int> State_Read::get_parameter(const std::string name_parameter) const {
    if (name_parameter == "State 0"){
        return state_0;
    }
    if (name_parameter == "State 1"){
        return state_1;
    }
    if (name_parameter == "State 2"){
        return state_2;
    }
    if (name_parameter == "State 3"){
        return state_3;
    }
    if (name_parameter == "State 4"){
        return state_4;
    }
    if (name_parameter == "State 5"){
        return state_5;
    }

    else{
        std::cerr << "Parameter name not define, use valida name!" << std::endl;
        throw;
    }
}
