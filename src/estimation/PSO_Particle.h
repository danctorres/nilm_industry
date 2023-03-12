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
    PSO_Particle(std::vector<int> &position, std::vector<int> &velocity, int fitness);

    // Setters
    void set_position(std::vector<int> &position);
    void set_velocity(std::vector<int> &velocity);
    void set_fitness(int fitness);
    void set_best();
    void set_best(const PSO_Particle &particle);

    // Getters
    std::vector<int> get_position() const;
    std::vector<int> get_velocity() const;
    int get_fitness() const;
    PSO_Best_Particle get_best() const;
private:
    std::vector<int> position;
    std::vector<int> velocity;
    int fitness;
    PSO_Best_Particle p_best;
};

#endif //DISSERTATION_NILM_PSO_PARTICLE_H
