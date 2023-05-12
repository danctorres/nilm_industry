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
    std::vector<double> get_eq(const int eq_idx) const;

    void denormalize(std::vector<double> &est_vec, const double min_agg, const double max_agg);
    void denormalize_all(const double min_agg, const double max_agg);
    void denormalize_minmax(std::vector<double> &est_vec, const double min, const double max);
    void denormalize_all_specific();
private:
    std::vector<double> est_eq0;
    std::vector<double> est_eq1;
    std::vector<double> est_eq2;
    std::vector<double> est_eq3;
    std::vector<double> est_eq4;
    std::vector<double> est_eq5;
};


#endif //NILM_INDUSTRY_ESTIMATIONS_H
