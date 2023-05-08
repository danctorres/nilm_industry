//
// Created by danctorres on 3/11/23.
//

#include "Matrix_W.h"


void Matrix_W::set_coefficients(const std::vector<float> &coef_0, const std::vector<float> &coef_1,
                                const std::vector<float> &coef_2, const std::vector<float> &coef_3,
                                const std::vector<float> &coef_4, const std::vector<float> &coef_5) {
    this->coef_0 = coef_0;
    this->coef_1 = coef_1;
    this->coef_2 = coef_2;
    this->coef_3 = coef_3;
    this->coef_4 = coef_4;
    this->coef_5 = coef_5;
}

void Matrix_W::set_coefficients(const std::vector<float> &coef, const int equipment_number) {
    switch (equipment_number) {
        case 0:
            this->coef_0 = coef;
            break;
        case 1:
            this->coef_1 = coef;
            break;
        case 2:
            this->coef_2 = coef;
            break;
        case 3:
            this->coef_3 = coef;
            break;
        case 4:
            this->coef_4 = coef;
            break;
        case 5:
            this->coef_5 = coef;
            break;
        default:
            std::cerr << "Use valid equipment number!" << std::endl;
            throw;
    }
}

std::vector<float> Matrix_W::get_coefficients(const int equipment_number) const {
    switch (equipment_number) {
        case 0:
            return coef_0;
        case 1:
            return coef_1;
        case 2:
            return coef_2;
        case 3:
            return coef_3;
        case 4:
            return coef_4;
        case 5:
            return coef_5;
        default:
            std::cerr << "Use valid equipment number!" << std::endl;
            throw;
    }
}

void Matrix_W::sum(const std::vector<float> &coef_0, const std::vector<float> &coef_1,
                   const std::vector<float> &coef_2, const std::vector<float> &coef_3,
                   const std::vector<float> &coef_4, const std::vector<float> &coef_5) {
    std::transform (this->coef_0.begin(), this->coef_0.end(), coef_0.begin(), this->coef_0.begin(), std::plus<float>());
    std::transform (this->coef_1.begin(), this->coef_1.end(), coef_1.begin(), this->coef_1.begin(), std::plus<float>());
    std::transform (this->coef_2.begin(), this->coef_2.end(), coef_2.begin(), this->coef_2.begin(), std::plus<float>());
    std::transform (this->coef_3.begin(), this->coef_3.end(), coef_3.begin(), this->coef_3.begin(), std::plus<float>());
    std::transform (this->coef_4.begin(), this->coef_4.end(), coef_4.begin(), this->coef_4.begin(), std::plus<float>());
    std::transform (this->coef_5.begin(), this->coef_5.end(), coef_5.begin(), this->coef_5.begin(), std::plus<float>());
}

void Matrix_W::sum(const std::vector<float> &coef, const int equipment_number) {
    switch(equipment_number) {
        case 0:
            std::transform (this->coef_0.begin(), this->coef_0.end(), coef.begin(), this->coef_0.begin(), std::plus<float>());
            break;
        case 1:
            std::transform (this->coef_1.begin(), this->coef_1.end(), coef.begin(), this->coef_1.begin(), std::plus<float>());
            break;
        case 2:
            std::transform (this->coef_2.begin(), this->coef_2.end(), coef.begin(), this->coef_2.begin(), std::plus<float>());
            break;
        case 3:
            std::transform (this->coef_3.begin(), this->coef_3.end(), coef.begin(), this->coef_3.begin(), std::plus<float>());
            break;
        case 4:
            std::transform (this->coef_4.begin(), this->coef_4.end(), coef.begin(), this->coef_4.begin(), std::plus<float>());
            break;
        case 5:
            std::transform (this->coef_5.begin(), this->coef_5.end(), coef.begin(), this->coef_5.begin(), std::plus<float>());
            break;
        default:
            std::cerr << "Use valid equipment idx!" << std::endl;
            throw;
    }
}
