//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"

// the quadratic objective function with quadratic penalty function weighted by a Lagrange multiplier
float objective_function(const std::vector<float> &pos) {
    float eq =  act[0] * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2)) +
                act[1] * (pos[3] + pos[4] * agg + pos[5] * pow(agg, 2)) +
                act[2] * (pos[6] + pos[7] * agg + pos[8] * pow(agg, 2)) +
                act[3] * (pos[9] + pos[10] * agg + pos[11] * pow(agg, 2)) +
                act[4] * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2)) +
                act[5] * (pos[15] + pos[16] * agg + pos[17] * pow(agg, 2));
    return pow(agg - eq, 2) + lambda * std::pow(std::max(0.0f, -eq), 2);
}
