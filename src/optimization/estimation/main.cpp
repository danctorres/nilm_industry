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

/*
 * #include "pso/PSO_Particle.h"
 * #include "simulated_annealing/SA.h"
 * #include "ant_colony/AC.h"
 * #include "genetic_algorithm/GA.h"
 * #include "newton/Newton.h"
 * #include "gradient_descent/GD.h"
 * #include "problem_formulation/Matrix_W.h"
 * #include "problem_formulation/objective_function.h"
*/

double agg = 0.0;
int act[number_equipment] = {0};
const float lambda = 1.0f;

// Values used for initializing the positions and the velocity vector of the PSO
std::vector<float> min_coef;
std::vector<float> max_coef;
// std::vector<float> max_eq_power = {2000.0f, 1500.0f, 6000.0f, 6000.0f, 100000.0f, 100000.0f};


void estimation(double *sum_est, int *num_ON, const float agg_sample, Read_State &st_data, int sample_idx, int number_equipment) {
    agg = agg_sample;

    for (int j = 0; j < number_equipment; j++) {
        act[j] = st_data.get_one_parameter(j, sample_idx);
    }

    auto pso = std::make_unique<PSO>(18000, 18, 200, 0.00001,
                                     min_coef, max_coef, 2.0f, 2.0f, 0.4f, 0.9f);
    pso->set_number_of_equipment(number_equipment);
    pso->run();

    /* for (auto &buff : pso->get_global_best().get_position()) {
        std::cout << " " << buff;
    }
    std::cout << std::endl; */

    // Calculations for the mean values of the coefficients
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
    const int number_equipment = 6;

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
            "../../../../data/processed/IMDELD/data_6_equipment/aggregate_training.csv");   // in this format for cmake
    auto agg_variant = agg_data->get_parameters("Active power");
    if (auto parameters = std::get_if < std::vector < float >> (&agg_variant)) {
        agg_vector = *parameters;
    }
    auto st_data = std::make_unique<Read_State>("../../../../data/processed/IMDELD/data_6_equipment/on_off_training.csv");


    /* // Ignore normalization
    // Normalize
    float agg_max = *max_element(agg_vector.begin(), agg_vector.end());
    float agg_min = *min_element(agg_vector.begin(), agg_vector.end());

    //float agg_max = 400000.0f;
    //float agg_min = 0.0f;

    for (auto &agg_elem: agg_vector) {
        agg_elem = (agg_elem - agg_min) / (agg_max - agg_min);
    }
    for (auto &eq_elem: max_eq_power) {
        eq_elem = (eq_elem - agg_min) / (agg_max - agg_min);
    }
    */

    // Initialize constants
    double sum_est[number_equipment * 3] = {0.0};     // sum of estimated coefficients
    int num_ON[number_equipment] = {0};                // number of ON samples

    if (argc > 1 && std::string(argv[1]) == "--parallel") {
        std::cout << "--- Running parallel optimization with openMP ---" << std::endl;
        #pragma omp parallel for
        for (int i = 0; i < agg_vector.size(); i++) {
            std::cout << "--- Estimation " << i << " ---" << std::endl;
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i, number_equipment);
        }
    }
    else {
        std::cout << "--- Running sequential optimization ---" << std::endl;
        // Iterate through training data
        for (int i = 0; i < agg_vector.size(); i++) {
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i, number_equipment);
        }
    }

    save_coef("../../../../results/optimization/IMDELD/estimated_coef.csv", sum_est, num_ON);
    return 0;
}


/*
// Metaheuristic optimization methods
std::vector<float> min_pos = {-100000, -100000};
std::vector<float> max_pos = {100000, 100000};

std::cout << std::endl << "--- PSO ---" << std::endl;
//auto start = std::chrono::high_resolution_clock::now(); // get start time
auto pso = std::make_unique<PSO>(20, 2, 100, 0.001, min_pos, max_pos,
                                 2.0f, 2.0f, 0.2f, 0.9f);
pso->run();
//auto stop = std::chrono::high_resolution_clock::now(); // get stop time
//auto duration = std::chrono::duration_cast< std::chrono::seconds>(stop - start); // calculate duration in microseconds
std::cout << "x: " << pso->get_global_best().get_position()[0] << ", y: " << pso->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << pso->get_global_best().get_fitness() << std::endl;
//std::cout << "Time taken by polynomial_function: " << duration.count() << " seconds" << std::endl;


std::cout << std::endl << "--- SIMULATED ANNEALING ---" << std::endl;
auto sa = std::make_unique<SA>(20, 2, 100, 0.001, min_pos, max_pos,
                               100000, 0.001f, 0.99f);
sa->run();
std::cout << "x: " << sa->get_global_best().get_position()[0] << ", y: " << sa->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << sa->get_global_best().get_fitness() << std::endl;


std::cout << std::endl << "--- ANT COLONY ---" << std::endl;
// The std cant be equal to 0, for the gaussian polynomial_function to work
auto acor = std::make_unique<AC>(20, 2, 100, 0.001, min_pos, max_pos,
                                 2, 0.001f, 0.85f, -5, 5);
acor->run();
std::cout << "x: " << acor->get_global_best().get_position()[0] << ", y: " << acor->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << acor->get_global_best().get_fitness() << std::endl;


std::cout << std::endl << "--- GENETIC ALGORITHM ---" << std::endl;
// int n_participants = n_particles / n_tournaments;
auto ga = std::make_unique<GA>(20, 2, 100, 0.001, min_pos, max_pos,
                               10, 0.5f, 1.0f , 0.5f, 1);
ga->run();
std::cout << "x: " << ga->get_global_best().get_position()[0] << ", y: " << ga->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << ga->get_global_best().get_fitness() << std::endl;


// Numerical optimization methods

std::cout << std::endl << "--- NEWTON ---" << std::endl;
auto newton = std::make_unique<Newton>(20, 2, 100, 0.001, min_pos, max_pos);
newton->run();
std::cout << "x: " << newton->get_global_best().get_position()[0] << ", y: " << newton->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << newton->get_global_best().get_fitness() << std::endl;


std::cout << std::endl << "--- GRADIENT DESCENT ---" << std::endl;
auto gd = std::make_unique<GD>(20, 2, 100, 0.001, min_pos, max_pos, 0.1f);
gd->run();
std::cout << "x: " << gd->get_global_best().get_position()[0] << ", y: " << gd->get_global_best().get_position()[1] << std::endl;
std::cout << "Fitness: " << gd->get_global_best().get_fitness() << std::endl;
*/

