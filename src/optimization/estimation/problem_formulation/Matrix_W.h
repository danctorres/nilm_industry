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
    void set_coefficients(const std::vector<float> &coef_0, const std::vector<float> &coef_1,
                          const std::vector<float> &coef_2, const std::vector<float> &coef_3,
                          const std::vector<float> &coef_4, const std::vector<float> &coef_5);
    void set_coefficients(const std::vector<float> &coef, const int equipment_number);

    std::vector<float> get_coefficients(const int equipment_number) const;

    void sum(const std::vector<float> &coef_0, const std::vector<float> &coef_1,
             const std::vector<float> &coef_2, const std::vector<float> &coef_3,
             const std::vector<float> &coef_4, const std::vector<float> &coef_5);
    void sum(const std::vector<float> &coef, const int equipment_number);

private:
    // Coefficients for the polynomial equipment polynomial_function
    std::vector<float> coef_0;
    std::vector<float> coef_1;
    std::vector<float> coef_2;
    std::vector<float> coef_3;
    std::vector<float> coef_4;
    std::vector<float> coef_5;
};


#endif //DISSERTATION_NILM_MATRIX_W_H
