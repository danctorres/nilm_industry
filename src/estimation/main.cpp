//
// Created by dtorres on 2/16/23.
//

#include <iostream>
#include <algorithm>
#include <memory>
#include "Read.cpp"
#include "Transform_Read.cpp"

int main(){
    auto data = std::make_unique<Transform_Read>();
    data->set_data("../../../data/processed/aggregate_training.csv");
    auto test = data->get_data();
    data->set_parameters();
    data->print_parameter(data->get_parameter("Timestamp"));
    return 0;
}
