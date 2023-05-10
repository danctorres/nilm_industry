//
// Created by danctorres on 10-05-2023.
//

#ifndef NILM_INDUSTRY_SAVE_COEF_H
#define NILM_INDUSTRY_SAVE_COEF_H

#include <fstream>
#include <iostream>
#include <string>

void save_coef(const std::string name, const float *sum_est, const int *num_ON);

#endif //NILM_INDUSTRY_SAVE_COEF_H
