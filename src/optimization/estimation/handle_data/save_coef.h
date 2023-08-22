//
// Created by danctorres on 10-05-2023.
//

#ifndef NILM_INDUSTRY_SAVE_COEF_H
#define NILM_INDUSTRY_SAVE_COEF_H

#include <cmath>
#include <fstream>
#include <iostream>
#include <string>

void save_coef(const std::string name, const double *new_coef, const int *num_ON, const int number_equipment, const double factor_round);

#endif //NILM_INDUSTRY_SAVE_COEF_H
