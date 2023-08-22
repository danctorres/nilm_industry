//
// Created by danctorres on 2/16/23.
//

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <omp.h>
#include <string>

#include "handle_data/Read.h"
#include "handle_data/Read_Aggregate.h"
#include "handle_data/Read_State.h"
#include "handle_data/Read_Coef.h"
#include "handle_data/save_coef.h"
#include "optimization_interface/Optimization.h"
#include "optimization_interface/Particle.h"
#include "pso/PSO.h"
#include "error/Error.h"
#include "polynomial_function/polynomial_function.h"

double agg = 0.0;
int act[number_equipment] = {0};
const float lambda = 1.0f;

void estimation(double *new_coef, int *num_ON, const float agg_sample, Read_State &st_data, int sample_idx, const int number_equipment, std::vector<float> min_coef, std::vector<float> max_coef) {
    agg = agg_sample;

    for (int j = 0; j < number_equipment; j++) {
        act[j] = st_data.get_one_parameter(j, sample_idx);
    }

    auto pso = std::make_unique<PSO>(number_equipment * 4 * 1000, 18, 200, 0.00001,
                                     min_coef, max_coef, 2.0f, 2.0f, 0.4f, 0.9f);


    pso->set_number_of_equipment(number_equipment);
    pso->run();

    for (int j = 0; j < number_equipment; j++) {
        if (act[j] == 1) {
            new_coef[j * 3] += pso->get_global_best().get_position()[j * 3];
            new_coef[j * 3 + 1] += pso->get_global_best().get_position()[j * 3 + 1];
            new_coef[j * 3 + 2] += pso->get_global_best().get_position()[j * 3 + 2];
            new_coef[j * 3 + 3] += pso->get_global_best().get_position()[j * 3 + 3];
            num_ON[j]++;
        }
    }
}

void save_coeff(const double *new_coef, int *num_ON, const int number_equipment, const double factor_round, auto &agg_vector, auto &st_data) {
    std::ifstream file("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv");
    if (file.good()) {
        std::vector<std::vector<double>> new_coefs_vec;
        for (int i = 0; i < number_equipment; ++i) {
            std::vector<double> new_coefs_vec_inner;
            for (int j = 0; j < 4; ++j) {
                new_coefs_vec_inner.push_back(new_coef[i * 4 + j]);
            }
            new_coefs_vec.push_back(new_coefs_vec_inner);
        }
        std::unique_ptr<Read_Coef> est_coef = std::make_unique<Read_Coef> ("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv");

        double error_est_old = 0.0;
        double error_est_new = 0.0;
        double eq_est_old = 0.0;
        double eq_est_new = 0.0;
        for (int i = 0; i < agg_vector.size(); i++) {
            for (int j = 0; j < number_equipment; j++) {
                eq_est_old += pol_func(agg_vector[i], st_data->get_one_parameter(j, i), est_coef->get_coef_eq(j));
                eq_est_new += pol_func(agg_vector[i], st_data->get_one_parameter(j, i), new_coefs_vec[j]);
            }
            error_est_old += std::abs(eq_est_old - agg_vector[i]);
            error_est_new += std::abs(eq_est_new - agg_vector[i]);
        }
        error_est_old = error_est_old / agg_vector.size();
        error_est_new = error_est_new / agg_vector.size();

        std::cout << "error_est_old" << error_est_old << std::endl;
        std::cout << "error_est_new" << error_est_new << std::endl;

        if (error_est_new < error_est_old) {
            std::cout << "--- Saving new coefficients ---" << std::endl;
            save_coef("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv", new_coef, num_ON, number_equipment, factor_round);
        }
    }
    else {
        std::cout << "--- Saving coefficients ---" << std::endl;
        save_coef("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv", new_coef, num_ON, number_equipment, factor_round);
    }
}


int main(int argc, char *argv[]) {
    const int number_equipment = 7;
    std::vector<float> min_coef;
    std::vector<float> max_coef;
    for (int l = 0; l < number_equipment; l++) {
        min_coef.push_back(-1.0f);
        min_coef.push_back(-1.0f);
        min_coef.push_back(-1.0f);
        min_coef.push_back(-1.0f);
        max_coef.push_back(1.0f);
        max_coef.push_back(1.0f);
        max_coef.push_back(1.0f);
        max_coef.push_back(1.0f);
    }

    std::vector<float> agg_vector;
    auto agg_data = std::make_unique<Read_Aggregate>(
            "../../../../data/processed/HIPE/1_week/aggregate_training/agg_training_" + std::to_string(number_equipment) + ".csv");
    auto agg_variant = agg_data->get_parameters("Active power");
    if (auto parameters = std::get_if < std::vector < float >> (&agg_variant)) {
        agg_vector = *parameters;
    }

    auto st_data = std::make_unique<Read_State>("../../../../data/processed/HIPE/1_week/state_training/st_training_" + std::to_string(number_equipment) + ".csv");

    double new_coef[number_equipment * 4] = {0.0};      // sum of estimated coefficients
    int num_ON[number_equipment] = {0};                 // number of ON samples
    const double factor_round = std::pow(10, 7);

    const int num_cycles = 5;
    if (argc > 1 && std::string(argv[1]) == "--parallel") {
        std::cout << "--- Running parallel optimization with openMP ---" << std::endl;
        for (int j = 0; j < num_cycles; j++) {
            for(int k = 0; k < number_equipment * 4; k++) {
                new_coef[k] = 0;
            }
            for(int k = 0; k < number_equipment; k++) {
                num_ON[k] = 0;
            }

            #pragma omp parallel for
            for (int i = 0; i < agg_vector.size(); i++) {
                // std::cout << "--- Estimation " << i << " ---" << std::endl;
                estimation(new_coef, num_ON, agg_vector[i], *st_data, i, number_equipment, min_coef, max_coef);
            }
            save_coeff(new_coef, num_ON, number_equipment, factor_round, agg_vector, st_data);
        }
    }
    else {
        std::cout << "--- Running sequential optimization ---" << std::endl;
        for (int j = 0; j < num_cycles; j++) {
            for(int k = 0; k < number_equipment * 4; k++) {
                new_coef[k] = 0;
            }
            for(int k = 0; k < number_equipment; k++) {
                num_ON[k] = 0;
            }

            // Iterate through training data
            for (int i = 0; i < agg_vector.size(); i++) {
                estimation(new_coef, num_ON, agg_vector[i], *st_data, i, number_equipment, min_coef, max_coef);
            }
            save_coeff(new_coef, num_ON, number_equipment, factor_round, agg_vector, st_data);
        }
    }
    return 0;
}
