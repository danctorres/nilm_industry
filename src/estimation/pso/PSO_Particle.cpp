//
// Created by dtorres on 3/11/23.
//

#include "PSO_Particle.h"

PSO_Particle::PSO_Particle() : Particle(), velocity(), personal_best() {}

PSO_Particle::PSO_Particle(const std::vector<float> velocity) : velocity(vel), personal_best(){}

PSO_Particle::PSO_Particle(const Particle &particle) {
    this->position = particle.get_position();
    this->fitness = particle.get_fitness();
    std::for_each(position.begin(), position.end(), [this](){velocity.push_back(0);});
    personal_best = *this;
}

PSO_Particle::PSO_Particle(const std::vector<float> &position, const std::vector<float> &velocity, const float fitness)
    personal_best = Particle(position, fitness);
    this->position = position;
    this->velocity = velocity;
    this->fitness = fitness;
}

void PSO_Particle::set_personal_best() {

}

void PSO_Particle::update_velocity(const std::vector<float> &velocity) : this->velocity(velocity) {}

void PSO_Particle::update_personal_best(){
    if (fitness > personal_best.get_fitness()){
        personal_best.set_position(position);
        personal_best.set_fitness(fitness);
    }
}

std::vector<float> PSO_Particle::get_velocity() const {
    return velocity;
}

Particle PSO_Particle::get_personal_best() const {
    return personal_best;
}

