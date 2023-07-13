//
// Created by danctorres on 08-05-2023.
//

#ifndef NILM_INDUSTRY_ESTIMATIONS_H
#define NILM_INDUSTRY_ESTIMATIONS_H

#include <algorithm>
#include <iostream>
#include <vector>

class Estimations {
public:
    Estimations();

    void set_est(const double est_eq, const int eq_idx);
    void set_min_max_eq(const std::vector<double> &min_eq, const std::vector<double> &max_eq);

    std::vector<double> get_eq(const int eq_idx) const;

    void denormalize(std::vector<double> &est_vec, const double min_agg, const double max_agg);
    void denormalize_all(const double min_agg, const double max_agg);
    void denormalize_minmax(std::vector<double> &est_vec, const double min, const double max);
    void denormalize_all_specific();
private:
    std::vector<std::vector<double>> est_eq;
    std::vector<double> min_eq;
    std::vector<double> max_eq;
};


#endif //NILM_INDUSTRY_ESTIMATIONS_H
