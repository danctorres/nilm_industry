//
// Created by dtorres on 3/1/23.
//

#include "Read.h"
#include <iostream>
#include <fstream>

Read::Read() {
    timestamp.push_back(0);
    active_power.push_back(0);
    reactive_power.push_back(0);
    apparent_power.push_back(0);
    current.push_back(0);
    voltage.push_back(0);
    power_factor.push_back(0);
}

void Read::read_file(std::string name_file) {
    std::fstream fin;
    fin.open(name_file, std::ios::in);

    if (!fin) std::cerr << "Could not open the file!" << std::endl;
    else{
        std::vector<std::string> row;
        std::string line;


        while(!fin.eof()){
            getline(fin, line);
            // std::cout << "Reading: " << line << std::endl;
        }

        fin.close();
    }
}

void Read::set_timestamp(std::vector<int> &timestamp) {
    this->timestamp = std::move(timestamp);
}

void Read::set_active_power(std::vector<int> &active_power) {
    this->active_power =std::move(active_power);
}

void Read::set_reactive_power(std::vector<int> &reactive_power) {
    this->reactive_power = std::move(reactive_power);
}

void Read::set_apparent_power(std::vector<int> &apparent_power) {
    this->apparent_power = std::move(apparent_power);
}

void Read::set_current(std::vector<int> &current) {
    this->current = std::move(current);
}

void Read::set_voltage(std::vector<int> &voltage) {
    this->voltage = std::move(voltage);
}

void Read::set_power_factor(std::vector<int> &power_factor) {
    this->power_factor = std::move(power_factor);
}


void Read::add_timestamp(int timestamp) {
    this->timestamp.push_back(timestamp);
}

void Read::add_active_power(int active_power) {
    this->active_power.push_back(active_power);
}

void Read::add_reactive_power(int reactive_power) {
    this->reactive_power.push_back(reactive_power);
}

void Read::add_current(int current) {
    this->current.push_back(current);
}

void Read::add_voltage(int voltage) {
    this->voltage.push_back(voltage);
}

void Read::add_power_factor(int power_factor) {
    this->power_factor.push_back(power_factor);
}


std::vector<int> Read::get_parameter(const std::string &name_parameter) const {
    if (name_parameter == "Timestamp"){
        return timestamp;
    }
    if (name_parameter == "Active Power"){
        return active_power;
    }
    if (name_parameter == "Reactive Power"){
        return reactive_power;
    }
    if (name_parameter == "Apparent Power"){
        return apparent_power;
    }
    if (name_parameter == "Current"){
        return current;
    }
    if (name_parameter == "Voltage"){
        return voltage;
    }
    if (name_parameter == "Power Factor"){
        return power_factor;
    }
    else{
        std::cout << "Parameter name not define, use valida name!" << std::endl;
        throw;
    }
}

void Read::print_parameter(const std::vector<int> &parameter) const {
    for (int values: parameter){
        std::cout << values << std::endl;
    }
}


Read::~Read() {
    std::cout << "Destructor" << std::endl;
}