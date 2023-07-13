//
// Created by danctorres on 3/7/2023.
//

#include "Read_State.h"


Read_State::Read_State(const std::string &name_file) : Read(name_file) {
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int j = 1; j < data[1].size(); j++) {
        std::vector<int> innerVector;
        states.push_back(innerVector);
        for (int i = 1; i < data.size() - 1; i++) {
            states[j - 1].push_back(std::stoi(data[i][j]));
        }
    }
}

std::vector<int> Read_State::get_parameters(const int eq_idx) const {
    return states[eq_idx];
}

int Read_State::get_one_parameter(const int eq_idx, const int sample) const {
    // std::cout << states[sample][eq_idx] << std::endl;
    return states[eq_idx][sample];
}

std::vector<std::vector<int>> Read_State::get_all_parameter() const {
    return states;
}
