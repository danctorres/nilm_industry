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
#include "newton/Newton.h"
#include "ant_colony/AC.h"
#include "genetic_algorithm/GA.h"


int main(){
    // Read training aggregate data
    //auto agg_data = std::make_unique<Read_Aggregate>("../../data/processed/aggregate_training.csv");
    auto agg_data = std::make_unique<Read_Aggregate> ("../../../data/processed/data_8_equipment/aggregate_training.csv");
    auto timestamps = agg_data->get_parameter ("Timestamp");
    //agg_data->print_parameter(timestamps);
    //auto st_data = std::make_unique<Read_State>("../../../data/processed/data_8_equipment/on_off_training.csv");
    //st_data->print_parameter(st_data->get_parameter("State 0"));

    //auto start = std::chrono::high_resolution_clock::now(); // get start time
    std::cout << std::endl << "--- PSO ---" << std::endl;

    std::vector<float> min_pos = {-10.0f, -10.0f};
    std::vector<float> max_pos = {10.0f, 10.0f};

    auto pso = std::make_unique<PSO>(20, 2, 100, 0.001, min_pos, max_pos, 2.0f, 2.0f, 0.2f, 0.9f);
    pso->run();

    //auto stop = std::chrono::high_resolution_clock::now(); // get stop time
    //auto duration = std::chrono::duration_cast< std::chrono::seconds>(stop - start); // calculate duration in microseconds
    std::cout << "x: " << pso->get_global_best().get_position()[0] << ", y: " << pso->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << pso->get_global_best().get_fitness() << std::endl;
    //std::cout << "Time taken by function: " << duration.count() << " seconds" << std::endl;

    std::cout << std::endl << "--- SIMULATED ANNEALING ---" << std::endl;
    auto sa = std::make_unique<SA>(20, 2, 100, 0.001, min_pos, max_pos, 5.0f, 0.001f, 0.99f);
    sa->run();
    std::cout << "x: " << sa->get_global_best().get_position()[0] << ", y: " << sa->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << sa->get_global_best().get_fitness() << std::endl;


    std::cout << std::endl << "--- NEWTON ---" << std::endl;
    auto newton = std::make_unique<Newton>(20, 2, 100, 0.001, min_pos, max_pos);
    newton->run();
    std::cout << "x: " << newton->get_global_best().get_position()[0] << ", y: " << newton->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << newton->get_global_best().get_fitness() << std::endl;


    std::cout << std::endl << "--- ANT COLONY ---" << std::endl;
    // The std cant be equal to 0, for the gaussian function to work
    auto acor = std::make_unique<AC>(20, 2, 100, 0.001, min_pos, max_pos, 2, 0.001f, 0.85f, -5, 5);
    acor->run();
    std::cout << "x: " << acor->get_global_best().get_position()[0] << ", y: " << acor->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << acor->get_global_best().get_fitness() << std::endl;


    std::cout << std::endl << "--- GENETIC ALGORITHM ---" << std::endl;
    // int n_participants = n_particles / n_tournaments;
    auto ga = std::make_unique<GA>(20, 2, 100, 0.001, min_pos, max_pos, 10, 0.5f, 1.0f , 0.5f, 1);
    ga->run();
    std::cout << "x: " << ga->get_global_best().get_position()[0] << ", y: " << ga->get_global_best().get_position()[1] << std::endl;
    std::cout << "Fitness: " << ga->get_global_best().get_fitness() << std::endl;

    return 0;
}
