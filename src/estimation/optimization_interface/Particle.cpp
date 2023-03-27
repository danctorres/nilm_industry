//
// Created by dtorres on 3/19/2023.
//

#include "Particle.h"

Particle::Particle() : position(), fitness(0) {}

Particle::Particle(std::vector<float> &pos) : position(pos), fitness(0){}

Particle::Particle(std::vector<float> &position, float fitness) {
    this->position = position;
    this->fitness = fitness;
}

void Particle::set_position(const std::vector<float> &position) {
    this->position = position;
}

void Particle::set_fitness(const float fitness) {
    this->fitness = fitness;
}

void Particle::set_parameters(const std::vector<float> &position, const float fitness) {
    this->position = position;
    this->fitness = fitness;
}

void Particle::set_parameters_Particle(const Particle &particle) {
    this->position = particle.get_position();
    this->fitness = particle.get_fitness();
}

std::vector<float> Particle::get_position() const{
    return position;
}

float Particle::get_fitness() const{
    return fitness;
}
