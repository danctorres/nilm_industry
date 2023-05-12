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

/* void Estimations::denormalize(std::vector<float> &est_vec) {
    auto min_val = *std::min_element(est_vec.begin(), est_vec.end());
    auto max_val = *std::max_element(est_vec.begin(), est_vec.end());

    for (int i = 0; i < est_vec.size(); i++) {
        est_vec[i] = est_vec[i] * (max_val - min_val) + min_val;
    }
} */

void Estimations::denormalize(std::vector<float> &est_vec, float min_agg, float max_agg) {
    for (auto &est : est_vec) {
        est = est * (max_agg - min_agg) + min_agg;
    }
}

void Estimations::denormalize_all(float min_agg, float max_agg) {
    denormalize(est_eq0, min_agg, max_agg);
    denormalize(est_eq1, min_agg, max_agg);
    denormalize(est_eq2, min_agg, max_agg);
    denormalize(est_eq3, min_agg, max_agg);
    denormalize(est_eq4, min_agg, max_agg);
    denormalize(est_eq5, min_agg, max_agg);
}

void Estimations::denormalize_minmax(std::vector<float> &est_vec, const float min, const float max) {
    for (auto& elem : est_vec) {
        //std::cout << " 1 elem: " << elem << std::endl;
        if (elem != 0) {
            elem = elem * (max - min) + min;
        }
    }
    /*for (auto& elem : est_vec) {
        std::cout << " 1 elem: " << elem << std::endl;
    }*/
}

void Estimations::denormalize_all_specific() {
    denormalize_minmax(est_eq0, 10.0f, 2000.0f);
    denormalize_minmax(est_eq1, 10.0f, 2000.0f);
    denormalize_minmax(est_eq2, 10.0f, 5000.0f);
    denormalize_minmax(est_eq3, 10.0f, 10000.0f);
    denormalize_minmax(est_eq4, 10.0f, 1000000.0f);
    denormalize_minmax(est_eq5, 10.0f, 1000000.0f);
}

Estimations::Estimations() {}
