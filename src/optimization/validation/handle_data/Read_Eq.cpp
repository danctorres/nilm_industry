//
// Created by danctorres on 08-05-2023.
//

#include "Read_Eq.h"

Read_Eq::Read_Eq(const std::string& name_file) : Read(name_file) {
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        actual_eq0.push_back(std::stof(data[i][1]));
        actual_eq1.push_back(std::stof(data[i][2]));
        actual_eq2.push_back(std::stof(data[i][3]));
        actual_eq3.push_back(std::stof(data[i][4]));
        actual_eq4.push_back(std::stof(data[i][5]));
        actual_eq5.push_back(std::stof(data[i][6]));
    }
}

std::vector<float> Read_Eq::get_eq(const int eq_idx) const {
    if (eq_idx == 0) {
        return actual_eq0;
    }
    else if (eq_idx == 1) {
        return actual_eq1;
    }
    else if (eq_idx == 2) {
        return actual_eq2;
    }
    else if (eq_idx == 3) {
        return actual_eq3;
    }
    else if (eq_idx == 4) {
        return actual_eq4;
    }
    else if (eq_idx == 5) {
        return actual_eq5;
    }
    else {
        std::cerr << "Parameter name not define, use valid name!" << std::endl;
        throw;
    }
}
