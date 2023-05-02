//
// Created by danctorres on 2/16/23.
//

#include <iostream>
#include <algorithm>
#include <string>
#include <chrono>
#include <memory>
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
std::vector<float> act;
const float lambda = 0.1f;

int main(){
    // Read training aggregate data
    //auto agg_data = std::make_unique<Read_Aggregate>("../../data/processed/aggregate_training.csv");
    //auto agg_data = std::make_unique<Read_Aggregate> ("../../../data/processed/data_8_equipment/aggregate_training.csv");   // in this format for cmake
    auto agg_data = std::make_unique<Read_Aggregate> ("../../../data/processed/data_6_equipment/aggregate_training.csv");   // in this format for cmake
    //auto timestamps = agg_data->get_parameter ("Timestamp");
    //agg_data->print_parameter(timestamps);
    //auto st_data = std::make_unique<Read_State>("../../../data/processed/data_8_equipment/on_off_training.csv");
    auto st_data = std::make_unique<Read_State>("../../../data/processed/data_6_equipment/on_off_training.csv");
    //st_data->print_parameter(st_data->get_parameters(0));
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
    //std::cout << "Time taken by function: " << duration.count() << " seconds" << std::endl;


    std::cout << std::endl << "--- SIMULATED ANNEALING ---" << std::endl;
    auto sa = std::make_unique<SA>(20, 2, 100, 0.001, min_pos, max_pos,
                                   100000, 0.001f, 0.99f);
    sa->run();
    std::cout << "x: " << sa->get_global_best().get_position()[0] << ", y: " << sa->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << sa->get_global_best().get_fitness() << std::endl;


    std::cout << std::endl << "--- ANT COLONY ---" << std::endl;
    // The std cant be equal to 0, for the gaussian function to work
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

    // For the 6 Equipment in the dataset, rank 4
    std::vector<float> min_coef = {-100000, -100000, -100000, -100000, -100000, -100000, -100000, -100000,
                                  -100000, -100000, -100000, -100000, -100000, -100000, -100000, -100000,
                                  -100000, -100000, -100000, -100000, -100000, -100000, -100000, -100000};
    std::vector<float> max_coef = {100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000,
                                  100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000,
                                  100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000};

    Matrix_W sum_est;
    std::vector<float> est_eq;

    // Iterate through training data
    for (int i = 0; i < agg_data->size(); i++) {
        agg = agg_data->get_one_parameter("Active power", i);
        std::cout << "Agg: " << agg << std::endl;

        // Iterate through each equipment
        for (int j = 0; j < 6; j++) {
            act.push_back(st_data->get_one_parameter(j, i));
            std::cout << "Eq: " << j << " act: " << act[j] << std::endl;
        }

        auto pso = std::make_unique<PSO>(240000, 24, 500, 1,
                                         min_coef, max_coef, 2.0f, 2.0f, 0.2f, 0.9f);
        pso->run();
        std::cout << "PSO run: " << i << " - fitness: " << pso->get_global_best().get_fitness() << std::endl;
        std::cout << "PSO run: " << i << " - pos 0: " << pso->get_global_best().get_position()[0] << std::endl;
        std::cout << "PSO run: " << i << " - pos 1: " << pso->get_global_best().get_position()[1] << std::endl;
        std::cout << "PSO run: " << i << " - pos 2: " << pso->get_global_best().get_position()[2] << std::endl;
        std::cout << "PSO run: " << i << " - pos 3: " << pso->get_global_best().get_position()[3] << std::endl;


        est_eq.insert(est_eq.end(), {pso->get_global_best().get_position()[0], pso->get_global_best().get_position()[1],
                                     pso->get_global_best().get_position()[2], pso->get_global_best().get_position()[3]});

        sum_est.set_coefficients(est_eq, 0);
        for (int j = 1; j < 6; j++) {
            est_eq.insert(est_eq.end(), {pso->get_global_best().get_position()[j * 4],
                                                 pso->get_global_best().get_position()[j * 4 + 1],
                                                 pso->get_global_best().get_position()[j * 4 + 2],
                                                 pso->get_global_best().get_position()[j * 4 + 3]});
            sum_est.set_coefficients(est_eq, j);
            sum_est.sum(est_eq, j);

            est_eq.clear();
        }
        act.clear();
    }

    for (int i = 0; i < 6; i++) {
        std::cout << "c" << i << "0: " << sum_est.get_coefficients(i)[0] / agg_data->size() << std::endl;
        std::cout << "c " << i << "1: " << sum_est.get_coefficients(i)[1] / agg_data->size() << std::endl;
        std::cout << "c" << i << "2: " << sum_est.get_coefficients(i)[2] / agg_data->size() << std::endl;
        std::cout << "c" << i << "3: " << sum_est.get_coefficients(i)[3] / agg_data->size() << std::endl;
    }

    return 0;
}
