//
// Created by danctorres on 08-05-2023.
//

#ifndef NILM_INDUSTRY_ERROR_H
#define NILM_INDUSTRY_ERROR_H

#include <iostream>
#include <numeric>
#include <cmath>
#include <vector>

class Error {
public:
    Error(const std::vector<float> &estimated_values, const std::vector<float> &actual_values);

    void set_mae(const float mae);
    void set_mse(const float mse);
    void set_rmse(const float rmse);
    void set_r2(const float r2);

    float get_mae() const;
    float get_mse() const;
    float get_rmse() const;
    float get_r2() const;

private:
    float mae;
    float mse;
    float rmse;
    float r2;
};


#endif //NILM_INDUSTRY_ERROR_H
