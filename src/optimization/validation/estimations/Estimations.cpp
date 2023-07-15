//
// Created by danctorres on 08-05-2023.
//

#include "Estimations.h"

void Estimations::set_est(const double est_eq, const int eq_idx) {
    if (eq_idx >= this->est_eq.size()) {
        std::vector<double> innerVector;
        this->est_eq.push_back(innerVector);
    }
    this->est_eq[eq_idx].push_back(est_eq);
}

// void Estimations::set_min_max_eq(const std::vector<double> &min_eq, const std::vector<double> &max_eq) {
//     this->min_eq = min_eq;
//     this->max_eq = max_eq;
// }

std::vector<double> Estimations::get_eq(const int eq_idx) const {
    return est_eq[eq_idx];
}

std::vector<std::vector<double>> Estimations::get_eqs() const {
    return est_eq;
}

int Estimations::get_size_equipment() const {
    return est_eq.size();
}

/* void Estimations::denormalize(std::vector<float> &est_vec) {
    auto min_val = *std::min_element(est_vec.begin(), est_vec.end());
    auto max_val = *std::max_element(est_vec.begin(), est_vec.end());

    for (int i = 0; i < est_vec.size(); i++) {
        est_vec[i] = est_vec[i] * (max_val - min_val) + min_val;
    }
} */

// void Estimations::denormalize(std::vector<double> &est_vec, const double min_agg, const double max_agg) {
//     for (auto &est : est_vec) {
//         est = est * (max_agg - min_agg) + min_agg;
//     }
// }

// void Estimations::denormalize_all(const double min_agg, const double max_agg) {
//     for (int i = 0; i < est_eq.size(); i++) {
//         denormalize(est_eq[i], min_agg, max_agg);
//     }
// }

// void Estimations::denormalize_minmax(std::vector<double> &est_vec, const double min, const double max) {
//     for (auto& elem : est_vec) {
//         if (elem != 0) {
//             elem = elem * (max - min) + min;
//         }
//     }
// }

// void Estimations::denormalize_all_specific() {
//     for (int i = 0; i < est_eq.size(); i++) {
//         denormalize_minmax(est_eq[i], min_eq[i], max_eq[i]);
//     }
// }

Estimations::Estimations() {}
