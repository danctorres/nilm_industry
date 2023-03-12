//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <iostream>
#include <vector>

#include "Matrix_W.h"
#include "Read_Aggregate.h"
#include "Read_State.h"
#include "PSO_Particle.h"
#include "PSO_Best_Particle.h"

class PSO{
public:
    PSO(int rank, int n_particles, int max_iter, int c1, int c2, int w_min, int w_max, int v_max);

    // Setters
    void set_global_best();

    // Getters
    std::vector<PSO_Particle> get_particles() const;
    PSO_Best_Particle get_global_best() const;

private:
    // PSO constants
    int rank;           // rank of the polynomial function
    int n_particles;    // number of particles
    int max_iter;       // max number of algorithm iterations
    int c1;             // cognitive constant
    int c2;             // social constant
    int w_min;          // minimum inertia weight value
    int w_max;          // max inertia weight value
    int v_max;          // max velocity

    // Particles
    PSO_Best_Particle global_best;               // global best
    std::vector<PSO_Particle> particles;    // PSO particles

    // Objective function
    void objective_function();

};


#endif //DISSERTATION_NILM_PSO_H
