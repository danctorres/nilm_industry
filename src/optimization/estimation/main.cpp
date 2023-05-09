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

#include "read_data/Read.h"
#include "read_data/Read_Aggregate.h"
#include "read_data/Read_State.h"
#include "optimization_interface/Optimization.h"
#include "optimization_interface/Particle.h"
#include "pso/PSO_Particle.h"
#include "pso/PSO.h"
#include "simulated_annealing/SA.h"
#include "ant_colony/AC.h"
#include "genetic_algorithm/GA.h"
#include "newton/Newton.h"
#include "gradient_descent/GD.h"
#include "problem_formulation/Matrix_W.h"
#include "problem_formulation/objective_function.h"


float agg = 0.0f;
int act[6] = {0};
const float lambda = 1000;
std::vector<float> min_coef = {-1.0f, -1.0f, -200.0f,
                                -1.0f, -1.0f, -200.0f,
                                -1.0f, -1.0f, -200.0f,
                                -1.0f, -1.0f, -200.0f,
                                -1.0f, -1.0f, -200.0f,
                                -1.0f, -1.0f, -200.0f};
std::vector<float> max_coef = {1.0f, 1.0f, 200.0f,
                                1.0f, 1.0f, 200.0f,
                                1.0f, 1.0f, 200.0f,
                                1.0f, 1.0f, 200.0f,
                                1.0f, 1.0f, 200.0f,
                                1.0f, 1.0f, 200.0f};


void estimation(float *sum_est, int *num_ON, const float agg_sample, Read_State &st_data, int sample_idx) {
    agg = agg_sample;
    for (int j = 0; j < 6; j++) {
        act[j] = st_data.get_one_parameter(j, sample_idx);
    }

    auto pso = std::make_unique<PSO>(18000, 18, 200, 100,
                                     min_coef, max_coef, 2.0f, 2.0f, 0.4f, 0.9f);
    pso->run();

    // Calculations for the mean values of the coefficients
    for (int j = 0; j < 6; j++) {
        if (act[j] == 1) {
            sum_est[j * 3] += pso->get_global_best().get_position()[j * 3];
            sum_est[j * 3 + 1] += pso->get_global_best().get_position()[j * 3 + 1];
            sum_est[j * 3 + 2] += pso->get_global_best().get_position()[j * 3 + 2];
            num_ON[j]++;
        }
    }
}


void save_file(const std::string name, const float *sum_est, const int *num_ON) {
    std::ofstream outfile(name);
    if (outfile.is_open()) {
        outfile << "Coef 1, Coef 2, Coef 3" << "\n";
        for(int i = 0; i < 6; i++) {
            outfile << sum_est[i * 3] / num_ON[i]  << ", " << sum_est[i * 3 + 1] / num_ON[i] << ", " << sum_est[i * 3 + 2] / num_ON[i] << "\n";
        }
        outfile.close();
    }
    else {
        std::cout << "Error saving into file." << std::endl;
    }
}


int main(int argc, char *argv[]){
    auto agg_data = std::make_unique<Read_Aggregate> ("../../../../data/processed/data_6_equipment/aggregate_training.csv");   // in this format for cmake
    std::vector<float> agg_vector = agg_data->get_parameters("Active power");
    auto st_data = std::make_unique<Read_State>("../../../../data/processed/data_6_equipment/on_off_training.csv");

    // Normalize
    /* float agg_max = *max_element(agg_vector.begin(), agg_vector.end());
    float agg_min = *min_element(agg_vector.begin(), agg_vector.end());
    for (auto &agg_elem : agg_vector) {
        agg_elem = (agg_vector[sample_idx] - agg_min) / (agg_max - agg_min); // Normalized
    } */

    // Initialize constants
    float sum_est[18] = {0.0f};     // sum of estimated coefficients
    int num_ON[6] = {0};                // number of ON samples

    if (argc > 1 && std::string(argv[1]) == "--parallel") {
        std::cout << "--- Running parallel optimization with opencl ---" << std::endl;
        #pragma omp parallel for
        for (int i = 0; i < agg_data->size(); i++) {
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i);
        }
    }
    else {
        std::cout << "--- Running sequential optimization ---" << std::endl;
        // Iterate through training data
        for (int i = 0; i < agg_data->size(); i++) {
            estimation(sum_est, num_ON, agg_vector[i], *st_data, i);
        }
    }

    save_file("../../../../results/estimation/estimated_coef.csv", sum_est, num_ON);
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

