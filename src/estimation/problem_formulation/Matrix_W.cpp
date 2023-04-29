//
// Created by danctorres on 3/11/23.
//

#include <vector>
#include "Matrix_W.h"


void Matrix_W::set_coefficients(const std::vector<double> coef_0, const std::vector<double> coef_1,
                                const std::vector<double> coef_2, const std::vector<double> coef_3,
                                const std::vector<double> coef_4, const std::vector<double> coef_5,
                                const std::vector<double> coef_6, const std::vector<double> coef_7) {
    this->coef_0 = coef_0;
    this->coef_1 = coef_1;
    this->coef_2 = coef_2;
    this->coef_3 = coef_3;
    this->coef_4 = coef_4;
    this->coef_5 = coef_5;
    this->coef_6 = coef_6;
    this->coef_7 = coef_7;
}

void Matrix_W::set_coefficients(const std::vector<double> coef, const int equipment_number) {
    if (equipment_number == 0) {
        this->coef_0 = coef;
    }
    if (equipment_number == 1) {
        this->coef_1 = coef;
    }
    if (equipment_number == 2) {
        this->coef_2 = coef;
    }
    if (equipment_number == 3) {
        this->coef_3 = coef;
    }
    if (equipment_number == 4) {
        this->coef_4 = coef;
    }
    if (equipment_number == 5) {
        this->coef_5 = coef;
    }
    if (equipment_number == 6) {
        this->coef_6 = coef;
    }
    if (equipment_number == 7) {
        this->coef_7 = coef;
    }
    else {
        throw;
    }
}

std::vector<double> Matrix_W::get_coefficients(const int equipment_number) const {
    if (equipment_number == 0) {
        return coef_0;
    }
    if (equipment_number == 1) {
        return coef_1;
    }
    if (equipment_number == 2) {
        return coef_2;
    }
    if (equipment_number == 3) {
        return coef_3;
    }
    if (equipment_number == 4) {
        return coef_4;
    }
    if (equipment_number == 5) {
        return coef_5;
    }
    if (equipment_number == 6) {
        return coef_6;
    }
    if (equipment_number == 7) {
        return coef_7;
    }
    else {
        throw;
    }
}

void Matrix_W::sum(const std::vector<double> coef_0, const std::vector<double> coef_1,
                                const std::vector<double> coef_2, const std::vector<double> coef_3,
                                const std::vector<double> coef_4, const std::vector<double> coef_5,
                                const std::vector<double> coef_6, const std::vector<double> coef_7) {
    this->coef_0 = std::transform (this->coef_0.begin(), this->coef_0.end(), coef_0.begin(), coef_0.begin(), std::plus<double>());
    this->coef_1 = std::transform (this->coef_1.begin(), this->coef_1.end(), coef_1.begin(), coef_1.begin(), std::plus<double>());
    this->coef_2 = std::transform (this->coef_2.begin(), this->coef_2.end(), coef_2.begin(), coef_2.begin(), std::plus<double>());
    this->coef_3 = std::transform (this->coef_3.begin(), this->coef_3.end(), coef_3.begin(), coef_3.begin(), std::plus<double>());
    this->coef_4 = std::transform (this->coef_4.begin(), this->coef_4.end(), coef_4.begin(), coef_4.begin(), std::plus<double>());
    this->coef_5 = std::transform (this->coef_5.begin(), this->coef_5.end(), coef_5.begin(), coef_5.begin(), std::plus<double>());
    this->coef_6 = std::transform (this->coef_6.begin(), this->coef_6.end(), coef_6.begin(), coef_6.begin(), std::plus<double>());
    this->coef_7 = std::transform (this->coef_7.begin(), this->coef_7.end(), coef_7.begin(), coef_7.begin(), std::plus<double>());
}

void Matrix_W::sum(const std::vector<double> coef, const int equipment_number) {
    if (equipment_number == 0) {
        this->coef_0 = std::transform (this->coef_0.begin(), this->coef_0.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 1) {
        this->coef_1 = std::transform (this->coef_1.begin(), this->coef_1.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 2) {
        this->coef_2 = std::transform (this->coef_2.begin(), this->coef_2.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 3) {
        this->coef_3 = std::transform (this->coef_3.begin(), this->coef_3.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 4) {
        this->coef_4 = std::transform (this->coef_4.begin(), this->coef_4.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 5) {
        this->coef_5 = std::transform (this->coef_5.begin(), this->coef_5.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 6) {
        this->coef_6 = std::transform (this->coef_6.begin(), this->coef_6.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    if (equipment_number == 7) {
        this->coef_7 = std::transform (this->coef_7.begin(), this->coef_7.end(), coef.begin(), coef.begin(), std::plus<double>());
    }
    else {
        throw;
    }
}
