//
// Created by danctorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_MATRIX_W_H
#define DISSERTATION_NILM_MATRIX_W_H

#include <vector>

class Matrix_W {
public:
    void set_coefficients(const std::vector<double> coef_0, const std::vector<double> coef_1,
                          const std::vector<double> coef_2, const std::vector<double> coef_3,
                          const std::vector<double> coef_4, const std::vector<double> coef_5,
                          const std::vector<double> coef_6, const std::vector<double> coef_7);
    void set_coefficients(const std::vector<double> coef, const int equipment_number);
    std::vector<double> get_coefficients(const int equipment_number) const;

    void sum(const std::vector<double> coef_0, const std::vector<double> coef_1,
             const std::vector<double> coef_2, const std::vector<double> coef_3,
             const std::vector<double> coef_4, const std::vector<double> coef_5,
             const std::vector<double> coef_6, const std::vector<double> coef_7);
    void sum(const std::vector<double> coef, const int equipment_number);
private:
    // Coefficients for the polynomial equipment function
    std::vector<double> coef_0;
    std::vector<double> coef_1;
    std::vector<double> coef_2;
    std::vector<double> coef_3;
    std::vector<double> coef_4;
    std::vector<double> coef_5;
    std::vector<double> coef_6;
    std::vector<double> coef_7;
};


#endif //DISSERTATION_NILM_MATRIX_W_H
