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

    auto pso = std::make_unique<PSO>(1000, 2, 100, 2.0, 2.0, 0.2, 0.9, -10.0, 10.0);
    pso->run_pso();

    return 0;
}
