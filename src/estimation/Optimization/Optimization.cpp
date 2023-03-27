//
// Created by dtorres on 3/16/2023.
//
#include <cmath>

#include "Optimization.h"

Optimization::Optimization() {
    n_particles = 0;
    rank = 0;
    max_iter = 0;
}

Optimization::Optimization(int n_particles, int rank, int max_iter) {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
}

float Optimization::objective_function(std::vector<float> position){
    float fitness = 0.0;
    for(const auto &pos : position){
        fitness += pow(pos, 2);
    }
    return fitness;
}

void Optimization::set_n_particles(uint n_particles) {
    this->n_particles = n_particles;
}

void Optimization::set_rank(uint rank) {
    this->rank = rank;
}

void Optimization::set_max_iter(uint max_iter) {
    this->max_iter = max_iter;
}
