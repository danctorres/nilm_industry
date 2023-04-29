//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"


float objective_function(const std::vector<float> &pos) {
    return fabs (agg - (
            pos[0] * act[0] + pos[1] * agg * act[0] + pos[2] * pow(agg, 2) * act[0] +       // eq 0
            pos[3] * act[1] + pos[4] * agg * act[1] + pos[5] * pow(agg, 2) * act[1] +       // eq 1
            pos[6] * act[2] + pos[7] * agg * act[2] + pos[8] * pow(agg, 2) * act[2] +       // eq 2
            pos[9] * act[3] + pos[10] * agg * act[3] + pos[11] * pow(agg, 2) * act[3] +     // eq 4
            pos[12] * act[4] + pos[13] * agg * act[4] + pos[14] * pow(agg, 2) * act[4] +    // eq 5
            pos[15] * act[5] + pos[16] * agg * act[5] + pos[17] * pow(agg, 2) * act[5] +    // eq 6
            pos[18] * act[6] + pos[19] * agg * act[6] + pos[20] * pow(agg, 2) * act[6] +    // eq 7
            pos[21] * act[7] + pos[22] * agg * act[7] + pos[23] * pow(agg, 2) * act[7]      // eq 8
            ));
}
