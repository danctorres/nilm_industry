//
// Created by dtorres on 3/11/23.
//

#include "PSO_Best_Particle.h"
#include <limits.h>

PSO_Best_Particle::PSO_Best_Particle() {
    position.push_back(0);
    fitness = INT_MAX; // Minimization problem, initialize g_best has "infinite"
}

PSO_Best_Particle::PSO_Best_Particle(std::vector<float> position, float fitness) {
    this->position = position;
    this->fitness = fitness;
}

/*PSO_Best_Particle::PSO_Best_Particle(const PSO_Particle &particle) {
    this->position = particle.get_position();
    this->fitness = particle.get_fitness();
}*/

void PSO_Best_Particle::set_position(std::vector<float> position) {
    this->position = position;
}

void PSO_Best_Particle::set_fitness(float fitness) {
    this->fitness = fitness;
}

std::vector<float> PSO_Best_Particle::get_position() {
    return position;
}

float PSO_Best_Particle::get_fitness() {
    return fitness;
}
