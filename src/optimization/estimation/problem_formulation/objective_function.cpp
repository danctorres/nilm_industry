//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"


float penalty_calculation(double eq_prediction, double max_val) {
    if (eq_prediction < 0.0f) {
        return fabs(eq_prediction);
    }
    else {
        if (eq_prediction > max_val) {
            return eq_prediction - max_val;
        }
        else {
            return 0;
        }
    }
}

float penalty_calculation2(double eq_prediction) {
    if ( (eq_prediction < 0.0f) ) {
        return pow(2.5 * eq_prediction, 2);
    }
    else {
        return 0;
    }
}

// float penalty_calculation3(double eq_prediction, double max_val) {
//     if ( (eq_prediction < 0.0f) || (eq_prediction > max_val)) {
//         return pow(24 * eq_prediction, 2);
//     }
//     else {
//         return 0;
//     }
// }

// the quadratic objective polynomial function with quadratic penalty polynomial function weighted by a Lagrange multiplier
double objective_function(const std::vector<double> &pos) {
    float eq_pred[pos.size()];
    float eq_pred_sum = 0.0f;
    float penalty = 0.0f;

    for (int i = 0; i < pos.size(); i++) {
        eq_pred[i] = static_cast<float>(act[i]) * (pos[i] + pos[i + 1] * agg + pos[i + 2] * pow(agg, 2));
        eq_pred_sum += eq_pred[i];
        penalty += penalty_calculation2(eq_pred[i]);
    }

    return pow(agg - eq_pred_sum, 2) + lambda * penalty;
}
