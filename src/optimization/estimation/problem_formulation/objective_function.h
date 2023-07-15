//
// Created by danctorres on 4/29/2023.
//

#ifndef DISSERTATION_NILM_OBJECTIVE_FUNCTION_H
#define DISSERTATION_NILM_OBJECTIVE_FUNCTION_H

#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

const int number_equipment = 2;     // needs to be redefined
extern double agg;
extern int act[number_equipment];
extern const float lambda;
// extern std::vector<float> max_eq_power;

double objective_function(const std::vector<double> &position);

#endif //DISSERTATION_NILM_OBJECTIVE_FUNCTION_H
