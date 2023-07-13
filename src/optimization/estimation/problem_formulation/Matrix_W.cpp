//
// Created by danctorres on 3/11/23.
//

#include "Matrix_W.h"


void Matrix_W::set_coefficients(const std::vector<std::vector<float>> &coefs) {
    this->coefs = coefs;
}

void Matrix_W::set_coefficients(const std::vector<float> &coef, const int equipment_number) {
    coefs[equipment_number] = coef;
}

std::vector<float> Matrix_W::get_coefficients(const int equipment_number) const {
    return coefs[equipment_number];
}

void Matrix_W::sum(const std::vector<float> &coef, const int equipment_number) {
    std::transform (this->coefs[equipment_number].begin(), this->coefs[equipment_number].end(), coef.begin(), this->coefs[equipment_number].begin(), std::plus<float>());
}
