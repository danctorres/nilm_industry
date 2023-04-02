//
// Created by dtorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <vector>
#include "../optimization_interface/Optimization.h"
#include "../optimization_interface/Particle.h"
#include "PSO_Particle.h"

class PSO : public Optimization{
public:
    PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, int lower_bound, int upper_bound);

    void adapter_particles_pso();
    void adapter_pso_particles();
    void initialize_velocities();
    void initialize_personal_best();
    void set_vmax(const float lower_bound, const float upper_bound);

    std::vector<PSO_Particle> get_particles() const;

    void update_personal_best();
    void run();

private:
    float c1;             // cognitive constant
    float c2;             // social constant
    float w_min;          // minimum inertia weight value
    float w_max;          // max inertia weight value
    float v_max;          // max velocity
    std::vector<PSO_Particle> pso_particles;
};


#endif //DISSERTATION_NILM_PSO_H
