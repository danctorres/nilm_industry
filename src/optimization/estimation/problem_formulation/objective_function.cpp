//
// Created by danctorres on 4/29/2023.
//

#include "objective_function.h"

// the quadratic objective polynomial function with quadratic penalty polynomial function weighted by a Lagrange multiplier
float objective_function(const std::vector<float> &pos) {
    float eq_0 = static_cast<float>(act[0]) * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2));
    float eq_1 = static_cast<float>(act[1]) * (pos[3] + pos[4] * agg + pos[5] * pow(agg, 2));
    float eq_2 = static_cast<float>(act[2]) * (pos[6] + pos[7] * agg + pos[8] * pow(agg, 2));
    float eq_3 = static_cast<float>(act[3]) * (pos[9] + pos[10] * agg + pos[11] * pow(agg, 2));
    float eq_4 = static_cast<float>(act[4]) * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2));
    float eq_5 = static_cast<float>(act[5]) * (pos[15] + pos[16] * agg + pos[17] * pow(agg, 2));
    float eq =  eq_0 + eq_1 + eq_2 + eq_3 + eq_4 + eq_5;

    float penalty = 0.0f;
    if( (eq_0 < 0.0f) || (eq_0 > max_eq_power[0]) ) {
        penalty += 0.1f;
    }
    if ( (eq_1 < 0.0f) || (eq_1 > max_eq_power[1]) ) {
        penalty += 0.1f;
    }
    if ( (eq_2 < 0.0f) || (eq_2 > max_eq_power[2]) ) {
        penalty += 0.1f;
    }
    if ( (eq_3 < 0.0f) || (eq_3 > max_eq_power[3]) ) {
        penalty += 0.1f;
    }
    if ( (eq_4 < 0.0f) || (eq_4 > max_eq_power[4]) ) {
        penalty += 0.1f;
    }
    if ( (eq_5 < 0.0f) || (eq_5 > max_eq_power[5]) ) {
        penalty += 0.1f;
    }

    /*float penalty = log(fmax(0.0f, -act[0] * (pos[0] + pos[1] * agg + pos[2] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[1] * (pos[3] + pos[4] * agg + pos[5] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[2] * (pos[6] + pos[7] * agg + pos[8] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[3] * (pos[9] + pos[10] * agg + pos[11] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[4] * (pos[12] + pos[13] * agg + pos[14] * pow(agg, 2))) + 1) +
                    log(fmax(0.0f, -act[5] * (pos[15] + pos[16] * agg + pos[17] * pow(agg, 2))) + 1); */
    //return log(pow(agg - eq, 2)) + lambda * (std::max(0.0f, -eq), 2));
    /* std::cout << "agg " << agg << " fabs(agg - eq) " << fabs(agg - eq) << " ------------------------- eq " << eq << " p " << lambda * penalty << std::endl;
    std::cout << "pos[0] " << pos[0] << " pos[1] " << pos[1] << "  pos[2] " <<  pos[2] << std::endl;
    std::cout << "pos[3] " << pos[3] << " pos[4] " << pos[4] << "  pos[5] " <<  pos[5] << std::endl;
    std::cout << "pos[6] " << pos[6] << " pos[7] " << pos[7] << "  pos[8] " <<  pos[8] << std::endl;
    std::cout << "pos[9] " << pos[9] << " pos[10] " << pos[10] << "  pos[11] " <<  pos[11] << std::endl;
    std::cout << "pos[12] " << pos[12] << " pos[13] " << pos[13] << "  pos[14] " <<  pos[14] << std::endl;
    std::cout << "pos[15] " << pos[15] << " pos[16] " << pos[16] << "  pos[17] " <<  pos[17] << std::endl;
    std::cout << "agg " << agg << " eq_0 " << eq_0 << " eq_1 " << eq_1 << "  eq_2 " <<  eq_2 << std::endl; */

    /*std::cout << "agg: " << agg << " max_eq_power[0]: " << max_eq_power[0] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl;
    std::cout << "agg: " << agg << " max_eq_power[1]: " << max_eq_power[1] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl;
    std::cout << "agg: " << agg << " max_eq_power[2]: " << max_eq_power[2] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl;
    std::cout << "agg: " << agg << " max_eq_power[3]: " << max_eq_power[3] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl;
    std::cout << "agg: " << agg << " max_eq_power[4]: " << max_eq_power[4] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl;
    std::cout << "agg: " << agg << " max_eq_power[5]: " << max_eq_power[5] << " pos[0]: " << pos[0] << " pos[1]: " << pos[1] << " pos[2]: " << pos[2] << " eq_1: " << ((eq_1 < 0.0f) || (eq_1 > max_eq_power[1]))  << " eq_1: " << eq_1 << " lambda * penalty  " << lambda * penalty << "  " << pow(agg - eq, 2) << " " << std::endl; */
    /*std::cout << "pos[3]: " << pos[3] << " pos[4]: " << pos[4] << " pos[5]: " << pos[5] << std::endl;
    std::cout << "eq_0: " << eq_0 << " eq_1: " << eq_1 << " eq_2: " << eq_2 << " eq_3: " << eq_3 << " eq_4: " << eq_4 << " eq_5: " << eq_5 << std::endl;
    std::cout << "penalty: " << penalty << std::endl;
    std::cout << "agg: " << agg << std::endl;
    std::cout << "eq: " << eq << std::endl;
    std::cout << "pow(agg - eq, 2): " << pow(agg - eq, 2) << std::endl;*/

    return pow(agg - eq, 2) + lambda * penalty;
}
