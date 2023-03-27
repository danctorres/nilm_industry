//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <iostream>
#include <vector>

#include "../read_data/Read_Aggregate.h"
#include "../read_data/Read_State.h"
#include "../Optimization/Optimization.h"
#include "../Matrix_W.h"
#include "PSO_Particle.h"
#include "PSO_Best_Particle.h"

class PSO : public Optimization {
public:
    PSO(int rank, int n_particles, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound);

    void set_vmax(const float lower_bound, const float upper_bound);

    std::vector<PSO_Particle> get_particles() const;
    PSO_Best_Particle get_global_best() const;

    void update_global_best();
    void run_pso();

private:
    // PSO constants
    float c1;             // cognitive constant
    float c2;             // social constant
    float w_min;          // minimum inertia weight value
    float w_max;          // max inertia weight value
    float v_max;          // max velocity

    // Particles
    PSO_Best_Particle global_best;               // global best
    std::vector<PSO_Particle> particles;    // PSO particles
};


#endif //DISSERTATION_NILM_PSO_H
