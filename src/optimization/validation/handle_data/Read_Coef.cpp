//
// Created by danctorres on 05/08/2023.
//

#include "Read_Coef.h"


Read_Coef::Read_Coef(const std::string &name_file) : Read(name_file) {
    const std::vector<std::vector<std::string>> data = this->get_data();
    for (int i = 1; i < data.size() - 1; i++){
        coef_0.push_back(std::stod(data[i][0]));
        coef_1.push_back(std::stod(data[i][1]));
        coef_2.push_back(std::stod(data[i][2]));
    }
}

std::vector<double> Read_Coef::get_coef_eq(const int eq_idx) const {
    std::vector<double> eq_coef = {coef_0[eq_idx], coef_1[eq_idx], coef_2[eq_idx]};
    return eq_coef;
}
