//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_BEST_PARTICLE_H
#define DISSERTATION_NILM_PSO_BEST_PARTICLE_H

#include <vector>
#include "PSO_Particle.h"

// Personal best and Global best
class PSO_Best_Particle{
public:
    // Constructor
    PSO_Best_Particle();
    PSO_Best_Particle(std::vector<int> position, int fitness);
    //PSO_Best_Particle(const PSO_Particle &particle);

    // Setters
    void set_position(std::vector<int> position);
    void set_fitness(int fitness);

    // Getters
    std::vector<int> get_position();
    int get_fitness();
private:
    std::vector<int> position;
    int fitness;
};

#endif //DISSERTATION_NILM_PSO_BEST_PARTICLE_H
