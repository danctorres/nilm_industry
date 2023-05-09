//
// Created by danctorres on 08-05-2023.
//

#include "polynomial_function.h"

double pol_func(const float agg, const int st, const std::vector<float> &coef) {
    // std::cout << "st " << st << " agg " << agg << " coef[0] " << coef[0] << " coef[1] " << coef[1] << " coef[2] " << coef[2] << std::endl;
    return st * (coef[0] + coef[1] * agg + coef[2] * pow(agg, 2));
}
