//
// Created by dtorres on 2/16/23.
//

#include <iostream>
#include <algorithm>
#include <memory>
#include <fstream>
#include "Read.cpp"

int main(){
    auto input_data = std::make_unique<Read>();

    std::vector<int> time;
    time.push_back(2);
    time.push_back(3);
    input_data->set_timestamp(time);
    input_data->add_timestamp(4);
    input_data->print_parameter(input_data->get_parameter("Timestamp"));

    input_data->read_file("../../../data/processed/aggregate_training.csv");

    return 0;
}
