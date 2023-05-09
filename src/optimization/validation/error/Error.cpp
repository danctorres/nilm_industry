//
// Created by danctorres on 08-05-2023.
//

#include "Error.h"

void Error::set_mae(const float mae) {
    this->mae = mae;
}

void Error::set_mse(const float mse) {
    this->mse = mse;
}

void Error::set_rmse(const float rmse) {
    this->rmse = rmse;
}

void Error::set_r2(const float r2) {
    this->r2 = r2;
}

float Error::get_mae() const {
    return mae;
}

float Error::get_mse() const {
    return mse;
}

float Error::get_rmse() const {
    return rmse;
}

float Error::get_r2() const {
    return r2;
}

Error::Error(const std::vector<float> &est, const std::vector<float> &actual) {
    double mae_buff = 0.0f;
    double mse_buff = 0.0f;
    double r2_buff = 0.0f;

    float act_mean = std::accumulate(actual.begin(), actual.end(), 0.0) / actual.size();

    for (int i = 0; i < est.size(); i++) {
        //std::cout << "Actual: " << actual[i]  << " Estimated: " << est[i] << std::endl;

        mae_buff += fabs(actual[i] - est[i]);
        mse_buff += pow(actual[i] - est[i], 2);

        r2_buff += pow(actual[i] - act_mean, 2);
    }

    mae = mae_buff / est.size();
    //std::cout << "mae_buff: " << mae_buff << " mae: " << mae << " est.size(): " << est.size() << std::endl;

    mse = mse_buff / est.size();
    rmse = std::sqrt(mse_buff / est.size());
    r2 = 1 - mse_buff / act_mean;
}
