//
// Created by danctorres on 3/7/2023.
//

#include "Read_State.h"


Read_State::Read_State(const std::string &name_file) : Read(name_file) {
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

std::vector<int> Read_State::get_parameters(const int eq_idx) const {
    switch(eq_idx) {
        case 0:
            return state_0;
        case 1:
            return state_1;
        case 2:
            return state_2;
        case 3:
            return state_3;
        case 4:
            return state_4;
        case 5:
            return state_5;
        default:
            std::cerr << "Use valid equipment idx!" << std::endl;
            throw;
    }
}

int Read_State::get_one_parameter(const int eq_idx, const int sample) const {
    switch (eq_idx) {
        case 0:
            return state_0[sample];
        case 1:
            return state_1[sample];
        case 2:
            return state_2[sample];
        case 3:
            return state_3[sample];
        case 4:
            return state_4[sample];
        case 5:
            return state_5[sample];
        default:
            std::cerr << "Use valid equipment idx!" << std::endl;
            throw;
    }
}

std::vector<std::vector<int>> Read_State::get_all_parameter() const {
    std::vector<std::vector<int>> data;
    data.push_back(state_0);    // Eq 1
    data.push_back(state_1);    // Eq 2
    data.push_back(state_2);    // Eq 3
    data.push_back(state_3);    // Eq 4
    data.push_back(state_4);    // Eq 7
    data.push_back(state_5);    // Eq 8
    return data;
}
