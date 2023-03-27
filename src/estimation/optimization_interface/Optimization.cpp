//
// Created by dtorres on 3/16/2023.
//
#include <algorithm>
#include <cmath>
#include <memory>


#include "Optimization.h"

Optimization::Optimization() : global_best(){
    n_particles = 0;
    rank = 0;
    max_iter = 0;
}

Optimization::Optimization(int n_particles, int rank, int max_iter) : global_best() {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
}

void Optimization::set_n_particles(int n_particles) {
    this->n_particles = n_particles;
}

void Optimization::set_rank(int rank) {
    this->rank = rank;
}

void Optimization::set_max_iter(int max_iter) {
    this->max_iter = max_iter;
}

void Optimization::set_global_best(const Particle &global_best) {
    this->global_best.set_parameters_Particle(global_best);
}

int Optimization::get_n_particles() const{
    return n_particles;
}

int Optimization::get_rank() const {
    return rank;
}

int Optimization::get_max_iter() const {
    return max_iter;
}

Particle Optimization::get_global_best() const {
    return global_best;
}

float Optimization::objective_function(std::vector<float> position){
    float fitness = 0.0;
    for(const auto &pos : position){
        fitness += pow(pos, 2);
    }
    return fitness;
}
