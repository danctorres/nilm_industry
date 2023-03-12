//
// Created by dtorres on 3/11/23.
//

#include "PSO_Best_Particle.h"

PSO_Best_Particle::PSO_Best_Particle() {
    position.push_back(0);
    fitness = 0;
}

PSO_Best_Particle::PSO_Best_Particle(std::vector<int> position, int fitness) {
    this->position = position;
    this->fitness = fitness;
}

/*PSO_Best_Particle::PSO_Best_Particle(const PSO_Particle &particle) {
    this->position = particle.get_position();
    this->fitness = particle.get_fitness();
}*/

void PSO_Best_Particle::set_position(std::vector<int> position) {
    this->position = position;
}

void PSO_Best_Particle::set_fitness(int fitness) {
    this->fitness = fitness;
}

std::vector<int> PSO_Best_Particle::get_position() {
    return position;
}

int PSO_Best_Particle::get_fitness() {
    return fitness;
}
