//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <vector>

#include "../optimization_interface/Optimization.h"
#include "../optimization_interface/Particle.h"
#include "PSO_Adapter.h"
#include "PSO_Particle.h"

class PSO : public Optimization, public PSO_Adapter {
public:
    PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound);

    void set_velocities();
    void set_vmax(const float lower_bound, const float upper_bound);

    std::vector<PSO_Particle> get_particles() const;
    PSO_Best_Particle get_global_best() const;

    void update_global_best();
    void run_pso();

private:
    float c1;             // cognitive constant
    float c2;             // social constant
    float w_min;          // minimum inertia weight value
    float w_max;          // max inertia weight value
    float v_max;          // max velocity
};


#endif //DISSERTATION_NILM_PSO_H
