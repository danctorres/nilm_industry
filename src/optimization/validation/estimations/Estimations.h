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

    void set_est(const float est_eq, const int eq_idx);
    std::vector<float> get_eq(const int eq_idx) const;

    void denormalize(std::vector<float> &est_vec);
    void denormalize_all();
private:
    std::vector<float> est_eq0;
    std::vector<float> est_eq1;
    std::vector<float> est_eq2;
    std::vector<float> est_eq3;
    std::vector<float> est_eq4;
    std::vector<float> est_eq5;
};


#endif //NILM_INDUSTRY_ESTIMATIONS_H
