//
// Created by danie on 3/7/2023.
//

#include <iostream>
#include <string>
#include <vector>
#include "Read_State.h"

Read_State::Read_State(const std::string &name_file) : Read(name_file){
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        state_0.push_back(std::stoi(data[i][0]));
        state_1.push_back(std::stoi(data[i][1]));
        state_2.push_back(std::stoi(data[i][2]));
        state_3.push_back(std::stoi(data[i][3]));
        state_4.push_back(std::stoi(data[i][4]));
        state_5.push_back(std::stoi(data[i][5]));
    }
}

std::vector<uint> Read_State::get_parameter(const std::string& name_parameter) const {
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

std::vector<std::vector<uint>> Read_State::get_all_parameter() const {
    std::vector<std::vector<uint>> data;
    data.push_back(state_0);
    data.push_back(state_1);
    data.push_back(state_2);
    data.push_back(state_3);
    data.push_back(state_4);
    data.push_back(state_5);
    return data;
}
