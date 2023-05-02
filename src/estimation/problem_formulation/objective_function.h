//
// Created by danctorres on 4/29/2023.
//

#ifndef DISSERTATION_NILM_OBJECTIVE_FUNCTION_H
#define DISSERTATION_NILM_OBJECTIVE_FUNCTION_H

#include <algorithm>
#include <cmath>
#include <vector>

extern float agg;
extern std::vector<float> act;
extern const float lambda;

float objective_function(const std::vector<float> &position);

#endif //DISSERTATION_NILM_OBJECTIVE_FUNCTION_H
