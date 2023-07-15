//
// Created by danctorres on 2/16/23.
//

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <memory>
#include <omp.h>
#include <string>

#include "handle_data/Read.h"
#include "handle_data/Read_Aggregate.h"
#include "handle_data/Read_State.h"
#include "handle_data/save_coef.h"
#include "optimization_interface/Optimization.h"
#include "optimization_interface/Particle.h"
#include "pso/PSO.h"

double agg = 0.0;
int act[number_equipment] = {0};
const float lambda = 1.0f;

void estimation(double *sum_est, int *num_ON, const float agg_sample, Read_State &st_data, int sample_idx, const int number_equipment, std::vector<float> min_coef, std::vector<float> max_coef) {
    agg = agg_sample;

    for (int j = 0; j < number_equipment; j++) {
        act[j] = st_data.get_one_parameter(j, sample_idx);
    }

    auto pso = std::make_unique<PSO>(18000, 18, 200, 0.00001,
                                     min_coef, max_coef, 2.0f, 2.0f, 0.4f, 0.9f);


    pso->set_number_of_equipment(number_equipment);
    pso->run();

    for (int j = 0; j < number_equipment; j++) {
        if (act[j] == 1) {
            sum_est[j * 3] += pso->get_global_best().get_position()[j * 3];
            sum_est[j * 3 + 1] += pso->get_global_best().get_position()[j * 3 + 1];
            sum_est[j * 3 + 2] += pso->get_global_best().get_position()[j * 3 + 2];
            num_ON[j]++;
        }
    }
}


int main(int argc, char *argv[]) {
    const int number_equipment = 9;

    std::vector<float> min_coef;
    std::vector<float> max_coef;
    for (int j = 0; j < number_equipment; j++) {
        min_coef.push_back(-1.0f);
        min_coef.push_back(-1.0f);
        min_coef.push_back(-1.0f);
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


    double sum_est[number_equipment * 3] = {0.0};     // sum of estimated coefficients
    int num_ON[number_equipment] = {0};                // number of ON samples
    
    if (argc > 1 && std::string(argv[1]) == "--parallel") {
        std::cout << "--- Running parallel optimization with openMP ---" << std::endl;
        #pragma omp parallel for
        for (int i = 0; i < agg_vector.size(); i++) {
            std::cout << "--- Estimation " << i << " ---" << std::endl;
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i, number_equipment, min_coef, max_coef);
        }
    }
    else {
        std::cout << "--- Running sequential optimization ---" << std::endl;
        // Iterate through training data
        for (int i = 0; i < agg_vector.size(); i++) {
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i, number_equipment, min_coef, max_coef);
        }
    }

    const double factor_round = std::pow(10, 7);
    save_coef("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv", sum_est, num_ON, number_equipment, factor_round);
    return 0;
}
