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
    Error(const std::vector<double> &estimated_values, const std::vector<float> &actual_values);

    void set_mae(const double mae);
    void set_mse(const double mse);
    void set_rmse(const double rmse);
    void set_r2(const double r2);

    double get_mae() const;
    double get_mse() const;
    double get_rmse() const;
    double get_r2() const;

private:
    double mae;
    double mse;
    double rmse;
    double r2;
};


#endif //NILM_INDUSTRY_ERROR_H
