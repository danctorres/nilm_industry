//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"

// the quadratic objective function with quadratic penalty function weighted by a Lagrange multiplier
float objective_function(const std::vector<float> &pos) {
    float eq = act[0] * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2) + pos[3] * pow(agg, 3)) +
            act[1] * (pos[4] + pos[5] * agg + pos[6] * pow(agg, 2) + pos[7] * pow(agg, 3)) +
            act[2] * (pos[8] + pos[9] * agg + pos[10] * pow(agg, 2) + pos[11] * pow(agg, 3)) +
            act[3] * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2) + pos[15] * pow(agg, 3)) +
            act[4] * (pos[16] + pos[17] * agg + pos[18] * pow(agg, 2) + pos[19] * pow(agg, 3)) +
            act[5] * (pos[20] + pos[21] * agg + pos[22] * pow(agg, 2) + pos[23] * pow(agg, 3));
    return pow(agg - eq, 2) + lambda * pow(std::max(0.0f, -eq), 2);
}
