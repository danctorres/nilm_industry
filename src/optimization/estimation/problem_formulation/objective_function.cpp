//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"

// the quadratic objective polynomial function with quadratic penalty polynomial function weighted by a Lagrange multiplier
float objective_function(const std::vector<float> &pos) {
    float eq =  act[0] * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2)) +
                act[1] * (pos[3] + pos[4] * agg + pos[5] * pow(agg, 2)) +
                act[2] * (pos[6] + pos[7] * agg + pos[8] * pow(agg, 2)) +
                act[3] * (pos[9] + pos[10] * agg + pos[11] * pow(agg, 2)) +
                act[4] * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2)) +
                act[5] * (pos[15] + pos[16] * agg + pos[17] * pow(agg, 2));
    float penalty = log(fmax(0.0f, -act[0] * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[1] * (pos[3] + pos[4] * agg + pos[5] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[2] * (pos[6] + pos[7] * agg + pos[8] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[3] * (pos[9] + pos[10] * agg + pos[11] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[4] * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[5] * (pos[15] + pos[16] * agg + pos[17] * pow(agg, 2))) + 1);
    //return log(pow(agg - eq, 2)) + lambda * (std::max(0.0f, -eq), 2));
    /*std::cout << "agg " << agg << " fabs(agg - eq) " << fabs(agg - eq) << " ------------------------- eq " << eq << " p " << lambda * penalty << std::endl;
    std::cout << "pos[0] " << pos[0] << " pos[1] " << pos[1] << "  pos[2] " <<  pos[2] << std::endl;
    std::cout << "pos[3] " << pos[3] << " pos[4] " << pos[4] << "  pos[5] " <<  pos[5] << std::endl;
    std::cout << "pos[6] " << pos[6] << " pos[7] " << pos[7] << "  pos[8] " <<  pos[8] << std::endl;
    std::cout << "pos[9] " << pos[9] << " pos[10] " << pos[10] << "  pos[11] " <<  pos[11] << std::endl;
    std::cout << "pos[12] " << pos[12] << " pos[13] " << pos[13] << "  pos[14] " <<  pos[14] << std::endl;
    std::cout << "pos[15] " << pos[15] << " pos[16] " << pos[16] << "  pos[17] " <<  pos[17] << std::endl;*/
    return pow(agg - eq, 2) + lambda * penalty;
}
