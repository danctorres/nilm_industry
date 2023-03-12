//
// Created by dtorres on 3/11/23.
//

#include "PSO_Particle.h"
#include "PSO_Best_Particle.h"

PSO_Particle::PSO_Particle() {
    position.push_back(0);
    velocity.push_back(0);
    fitness = 0;
    p_best = PSO_Best_Particle(position, fitness);
}

PSO_Particle::PSO_Particle(std::vector<int> &position, std::vector<int> &velocity, int fitness){
    this->position = position;
    this->velocity = velocity;
    this->fitness = fitness;
    p_best = PSO_Best_Particle(position, fitness);
}

void PSO_Particle::set_position(std::vector<int> &position) {
    this->position = position;
}

void PSO_Particle::set_velocity(std::vector<int> &velocity) {
    this->velocity = velocity;
}

void PSO_Particle::set_fitness(int fitness) {
    this->fitness = fitness;
}

void PSO_Particle::set_best() {
    p_best = PSO_Best_Particle(position, fitness);
}

void PSO_Particle::set_best(const PSO_Particle &particle){
    if (fitness <= particle.fitness){
        p_best = PSO_Best_Particle(particle.position, particle.fitness);
    }
}

std::vector<int> PSO_Particle::get_position() const {
    return position;
}

std::vector<int> PSO_Particle::get_velocity() const {
    return velocity;
}

int PSO_Particle::get_fitness() const {
    return fitness;
}

PSO_Best_Particle PSO_Particle::get_best() const {
    return p_best;
}
