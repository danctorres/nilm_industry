//
// Created by danctorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_MATRIX_W_H
#define DISSERTATION_NILM_MATRIX_W_H

#include <algorithm>
#include <iostream>
#include <vector>

class Matrix_W {
public:
    void set_coefficients(const std::vector<std::vector<float>> &coefs);
    void set_coefficients(const std::vector<float> &coef, const int equipment_number);

    std::vector<float> get_coefficients(const int equipment_number) const;

    void sum(const std::vector<float> &coef, const int equipment_number);

private:
    // Coefficients for the polynomial equipment polynomial_function
    int number_equipment;
    std::vector<std::vector<float>> coefs;
};


#endif //DISSERTATION_NILM_MATRIX_W_H
