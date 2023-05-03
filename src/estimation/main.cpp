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
const float lambda = 50000;

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
    std::vector<float> min_coef = {-10.0f, -10.0f, -100.0f,
                                   -10.0f, -10.0f, -100.0f,
                                   -10.0f, -10.0f, -100.0f,
                                   -10.0f, -10.0f, -100.0f,
                                   -10.0f, -10.0f, -100.0f,
                                   -10.0f, -10.0f, -100.0f};
    std::vector<float> max_coef = {10.0f, 10.0f, 100.0f,
                                   10.0f, 10.0f, 100.0f,
                                   10.0f, 10.0f, 100.0f,
                                   10.0f, 10.0f, 100.0f,
                                   10.0f, 10.0f, 100.0f,
                                   10.0f, 10.0f, 100.0f};

    Matrix_W sum_est;
    std::vector<float> est_eq;

    // Iterate through training data
    for (int i = 0; i < agg_data->size(); i++) {
        agg = agg_data->get_one_parameter("Active power", i);
        std::cout << std::endl << "Agg: " << agg << std::endl;

        // Iterate through each equipment
        for (int j = 0; j < 6; j++) {
            act.push_back(st_data->get_one_parameter(j, i));
            std::cout << "Eq " << j << " - " << act[j] << " ";
        }

        auto pso = std::make_unique<PSO>(180000, 18, 1000, 100,
                                         min_coef, max_coef, 2.0f, 2.0f, 0.4f, 0.9f);
        pso->run();
        std::cout << "PSO run: " << i << " - fitness: " << pso->get_global_best().get_fitness() << std::endl;
        std::cout << " - pos 0: " << pso->get_global_best().get_position()[0] << std::endl;
        std::cout << " - pos 1: " << pso->get_global_best().get_position()[1] << std::endl;
        std::cout << " - pos 2: " << pso->get_global_best().get_position()[2] << std::endl;

        std::cout << "Eq 1 " << act[0] << "- Est: " <<
        act[0] * (
                pso->get_global_best().get_position()[0] +
                pso->get_global_best().get_position()[1] * agg +
                pso->get_global_best().get_position()[2] * pow(agg, 2))
        << std::endl;


        for (int j = 0; j < 6; j++) {
            if (act[j] == 1) {
                est_eq.insert(est_eq.end(), {
                    pso->get_global_best().get_position()[j * 3],
                    pso->get_global_best().get_position()[j * 3 + 1],
                    pso->get_global_best().get_position()[j * 3 + 2]
                });
                sum_est.set_coefficients(est_eq, j);
                sum_est.sum(est_eq, j);
                est_eq.clear();
            }
        }
        act.clear();
    }

    for (int i = 0; i < 6; i++) {
        std::cout << "c" << i << "0: " << sum_est.get_coefficients(i)[0] / std::count(st_data->get_parameters(0).begin(), st_data->get_parameters(0).end(), 1) << std::endl;
        std::cout << "c" << i << "1: " << sum_est.get_coefficients(i)[1] / std::count(st_data->get_parameters(1).begin(), st_data->get_parameters(1).end(), 1) << std::endl;
        std::cout << "c" << i << "2: " << sum_est.get_coefficients(i)[2] / std::count(st_data->get_parameters(2).begin(), st_data->get_parameters(2).end(), 1) << std::endl;
        std::cout << "c" << i << "3: " << sum_est.get_coefficients(i)[3] / std::count(st_data->get_parameters(3).begin(), st_data->get_parameters(3).end(), 1) << std::endl;
        std::cout << "c" << i << "4: " << sum_est.get_coefficients(i)[4] / std::count(st_data->get_parameters(4).begin(), st_data->get_parameters(4).end(), 1) << std::endl;
        std::cout << "c" << i << "5: " << sum_est.get_coefficients(i)[5] / std::count(st_data->get_parameters(5).begin(), st_data->get_parameters(5).end(), 1) << std::endl;
    }

    return 0;
}
