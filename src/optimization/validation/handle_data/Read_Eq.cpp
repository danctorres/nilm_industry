//
// Created by danctorres on 08-05-2023.
//

#include "Read_Eq.h"

Read_Eq::Read_Eq(const std::string& name_file) : Read(name_file) {
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int j = 1; j < data[0].size(); j++) {
        if (j - 1 >= actual_eq.size()) {
            std::vector<float> innerVector;
            actual_eq.push_back(innerVector);
        }
        for (int i = 1; i < data.size() - 1; i++) {
            actual_eq[j - 1].push_back(std::stof(data[i][j]));

        }
    }
}

std::vector<float> Read_Eq::get_eq(const int eq_idx) const {
    return actual_eq[eq_idx];
}

std::vector<std::vector<float>> Read_Eq::get_eqs() const {
    return actual_eq;
}
