//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_PARTICLE_H
#define DISSERTATION_NILM_PSO_PARTICLE_H

#include <memory>
#include <vector>
#include "PSO_Best_Particle.h"
#include "PSO_Best_Particle.cpp"

// Represents the particles
class PSO_Particle{
public:
    PSO_Particle();
    PSO_Particle(std::vector<float> &position, std::vector<float> &velocity, float fitness);

    // Setters
    void set_position(std::vector<float> &position);
    void set_velocity(std::vector<float> &velocity);
    void set_fitness(float fitness);
    void set_best();
    void set_best(const PSO_Particle &particle);

    // Getters
    std::vector<float> get_position() const;
    std::vector<float> get_velocity() const;
    float get_fitness() const;
    PSO_Best_Particle get_best() const;

    void update_pbest();
private:
    std::vector<float> position;
    std::vector<float> velocity;
    float fitness;
    PSO_Best_Particle p_best;
};

#endif //DISSERTATION_NILM_PSO_PARTICLE_H
