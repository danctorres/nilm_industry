//
// Created by danctorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_H
#define DISSERTATION_NILM_PSO_H

#include <cmath>
#include <iostream>
#include <random>
#include <vector>
#include "../optimization_interface/Optimization.h"
#include "../optimization_interface/Particle.h"
#include "PSO_Particle.h"


class PSO : public Optimization{
public:
    PSO(const int n_particles, const int rank, const int max_iter, const float threshold,
        const std::vector<float> &min_pos, const std::vector<float> &max_pos, const float c1, const float c2,
        const float w_min, const float w_max);

    void set_c1(const float c1);
    void set_c2(const float c2);
    void set_w_min(const float w_min);
    void set_w_max(const float w_max);
    void set_v_max(const std::vector<float> &v_max);
    void set_v_max(const std::vector<float> &pos_min, const std::vector<float> &pos_max);
    void set_pso_particles(const std::vector<PSO_Particle> &pso_particles);

    float get_c1() const;
    float get_c2() const;
    float get_w_min() const;
    float get_w_max() const;
    std::vector<float> get_v_max() const;
    std::vector<PSO_Particle> get_pso_particles() const;


    void adapter_particles_pso();
    void adapter_pso_particles();
    void initialize_velocities();
    void initialize_personal_best();


    void update_personal_best();
    void run();

private:
    float c1;             // cognitive constant
    float c2;             // social constant
    float w_min;          // minimum inertia weight value
    float w_max;          // max inertia weight value
    std::vector<float> v_max;          // max velocity
    std::vector<PSO_Particle> pso_particles;
};


#endif //DISSERTATION_NILM_PSO_H
