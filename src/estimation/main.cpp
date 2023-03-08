//
// Created by dtorres on 2/16/23.
//

#include <iostream>
#include <algorithm>
#include <memory>
#include "Read.cpp"
#include "Aggregate_Read.cpp"
#include "State_Read.cpp"

int main(){
    auto a_data = std::make_unique<Aggregate_Read>();
    a_data->set_data("../../../data/processed/aggregate_training.csv");
    a_data->set_parameters();
    a_data->print_parameter(a_data->get_parameter("Timestamp"));

    auto s_data = std::make_unique<State_Read>();
    s_data->set_data("../../../data/processed/on_off_training.csv");
    s_data->set_parameters();
    s_data->print_parameter(s_data->get_parameter("State 0"));
    std::cout << std::endl << s_data->get_parameter("State 0").size() << std::endl;
    std::cout << std::endl << a_data->get_parameter("Timestamp").size() << std::endl;

    return 0;
}
