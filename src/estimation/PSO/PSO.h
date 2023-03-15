//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <iostream>
#include <vector>

#include "../Matrix_W.h"
#include "../read_data/Read_Aggregate.h"
#include "../read_data/Read_State.h"
#include "PSO_Particle.h"
#include "PSO_Best_Particle.h"

class PSO{
public:
    PSO(int rank, int n_particles, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound);

    // Setters
    void set_vmax(const float lower_bound, const float upper_bound);

    // Getters
    std::vector<PSO_Particle> get_particles() const;
    PSO_Best_Particle get_global_best() const;

    void update_global_best();
    void run_pso();

private:
    // PSO constants
    int rank;           // rank of the polynomial function
    int n_particles;    // number of particles
    int max_iter;       // max number of algorithm iterations
    float c1;             // cognitive constant
    float c2;             // social constant
    float w_min;          // minimum inertia weight value
    float w_max;          // max inertia weight value
    float v_max;          // max velocity

    // Particles
    PSO_Best_Particle global_best;               // global best
    std::vector<PSO_Particle> particles;    // PSO particles

    // Objective function
    float objective_function(std::vector<float> position);

};


#endif //DISSERTATION_NILM_PSO_H
