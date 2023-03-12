//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_MATRIX_W_H
#define DISSERTATION_NILM_MATRIX_W_H

#include <vector>

class Matrix_W {
public:
    std::vector<std::vector<int>> get_coefficients(int equipment_number);
    virtual void calculate_coefficients(std::vector<std::vector<int>> data);
private:
    // Coefficients for the polynomial equipment function
    std::vector<std::vector<int>> coef_0;
    std::vector<std::vector<int>> coef_1;
    std::vector<std::vector<int>> coef_2;
    std::vector<std::vector<int>> coef_3;
    std::vector<std::vector<int>> coef_4;
    std::vector<std::vector<int>> coef_5;
    std::vector<std::vector<int>> coef_6;
    std::vector<std::vector<int>> coef_7;
};


#endif //DISSERTATION_NILM_MATRIX_W_H
