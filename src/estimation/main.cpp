//
// Created by dtorres on 2/16/23.
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


int main(){
    // Read training aggregate data
    //auto agg_data = std::make_unique<Read_Aggregate>("../../data/processed/aggregate_training.csv");
    auto agg_data = std::make_unique<Read_Aggregate> ("../../../data/processed/data_8_equipment/aggregate_training.csv");
    auto timestamps = agg_data->get_parameter ("Timestamp");
    //agg_data->print_parameter(timestamps);
    //auto st_data = std::make_unique<Read_State>("../../../data/processed/data_8_equipment/on_off_training.csv");
    //st_data->print_parameter(st_data->get_parameter("State 0"));

    auto start = std::chrono::high_resolution_clock::now(); // get start time

    auto pso = std::make_unique<PSO>(10000, 2, 10000, 2.0, 2.0, 0.2, 0.9, -10, 10);
    pso->run();

    auto stop = std::chrono::high_resolution_clock::now(); // get stop time
    auto duration = std::chrono::duration_cast< std::chrono::seconds>(stop - start); // calculate duration in microseconds
    std::cout << "Time taken by function: " << duration.count() << " seconds" << std::endl;

    std::cout << "--- PSO Solution ---" << std::endl;
    std::cout << "Fitness: " << pso->get_global_best().get_fitness() << std::endl;
    std::cout << "x: " << pso->get_global_best().get_position()[0] << ", y: " << pso->get_global_best().get_position()[1] << std::endl;

    return 0;
}
