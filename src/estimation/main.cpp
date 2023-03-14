//
// Created by dtorres on 2/16/23.
//

#include <iostream>
#include <algorithm>
#include <chrono>
#include <memory>
#include "Read.cpp"
#include "Read_Aggregate.cpp"
#include "Read_State.cpp"
#include "PSO.cpp"

int main(){
    // Read training aggregate data
    auto a_data = std::make_unique<Read_Aggregate>();
    a_data->set_data("../../../data/processed/aggregate_training.csv");
    a_data->set_parameters();
    //a_data->print_parameter(a_data->get_parameter("Timestamp"));

    // Read training state data
    auto s_data = std::make_unique<Read_State>();
    s_data->set_data("../../../data/processed/on_off_training.csv");    // file path for cmake
    s_data->set_parameters();
    //s_data->print_parameter(s_data->get_parameter("State 0"));


    // Debug
    //std::cout << std::endl << s_data->get_parameter("State 0").size() << std::endl;
    //std::cout << std::endl << a_data->get_parameter("Timestamp").size() << std::endl;

    // PSO
    int rank = 2;
    int number_particles = 100;
    int max_iter = 20;
    float c1 = 2.0;
    float c2 = 2.0;
    float w_max = 0.9;
    float w_min = 0.2;

    int v_max = 10000;  // define later

    auto start_time = std::chrono::high_resolution_clock::now();
    PSO pso(rank, number_particles, max_iter, c1, c2, w_min, w_max, v_max);
    pso.run_pso();
    auto end_time = std::chrono::high_resolution_clock::now();


    std::cout << "Global best X: " << pso.get_global_best().get_position()[0] << " Y: " << pso.get_global_best().get_position()[1] << std::endl;
    std::cout << "Global best fitness: " << pso.get_global_best().get_fitness() << std::endl;

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Execution time: " << duration.count() << " milliseconds" << std::endl;
    return 0;
}
