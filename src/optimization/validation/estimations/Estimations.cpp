//
// Created by danctorres on 08-05-2023.
//

#include "Estimations.h"

void Estimations::set_est(const float est_eq, const int eq_idx) {
    switch(eq_idx) {
        case 0:
            this->est_eq0.push_back(est_eq);
            break;
        case 1:
            this->est_eq1.push_back(est_eq);
            break;
        case 2:
            this->est_eq2.push_back(est_eq);
            break;
        case 3:
            this->est_eq3.push_back(est_eq);
            break;
        case 4:
            this->est_eq4.push_back(est_eq);
            break;
        case 5:
            this->est_eq5.push_back(est_eq);
            break;
        default:
            std::cerr << "Use valid equipment idx to set the estimates!" << std::endl;
            throw;
    }
}

std::vector<float> Estimations::get_eq(const int eq_idx) const {
    switch(eq_idx) {
        case 0:
            return est_eq0;
        case 1:
            return est_eq1;
        case 2:
            return est_eq2;
        case 3:
            return est_eq3;
        case 4:
            return est_eq4;
        case 5:
            return est_eq5;
        default:
            std::cerr << "Use valid equipment idx!" << std::endl;
            throw;
    }
}

void Estimations::denormalize(std::vector<float> &est_vec) {
    auto max = std::max_element(est_vec.begin(), est_vec.end());
    auto min = std::min_element(est_vec.begin(), est_vec.end());

    for (auto& elem : est_vec) {
        elem = elem * (*max - *min) + *min;
    }
}

void Estimations::denormalize_all() {
    denormalize(est_eq0);
    denormalize(est_eq1);
    denormalize(est_eq2);
    denormalize(est_eq3);
    denormalize(est_eq4);
    denormalize(est_eq5);
}

Estimations::Estimations() {}
