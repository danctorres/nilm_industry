//
// Created by danctorres on 3/19/2023.
//

#include "Particle.h"


Particle::Particle() : position(), fitness(0.0) {}

Particle::Particle(const std::vector<double> &pos) : position(pos), fitness(0.0){}

Particle::Particle(const std::vector<double> &position, const double fitness) {
    this->position = position;
    this->fitness = fitness;
}

void Particle::set_position(const std::vector<double> &position) {
    this->position = position;
}

void Particle::set_fitness(const double fitness) {
    this->fitness = fitness;
}

void Particle::set_parameters(const std::vector<double> &position, const double fitness) {
    this->position = std::move(position);
    this->fitness = fitness;
}

void Particle::set_parameters_Particle(const Particle &particle) {
    this->position = particle.get_position();
    this->fitness = particle.get_fitness();
}

std::vector<double> Particle::get_position() const{
    return position;
}

double Particle::get_fitness() const{
    return fitness;
}
