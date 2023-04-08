//
// Created by danctorres on 3/11/23.
//

#ifndef DISSERTATION_NILM_PSO_PARTICLE_H
#define DISSERTATION_NILM_PSO_PARTICLE_H

#include <memory>
#include <vector>
#include "../optimization_interface/Particle.h"


class PSO_Particle : public Particle{
public:
    PSO_Particle();
    PSO_Particle(const std::vector<float> vel);
    PSO_Particle(const Particle &particle);
    PSO_Particle(const std::vector<float> &position, const std::vector<float> &velocity, const float fitness);

    void set_velocity(const std::vector<float> &velocity);
    void set_personal_best(const Particle &particle);

    void update_personal_best();

    std::vector<float> get_velocity() const;
    Particle get_personal_best() const;

private:
    std::vector<float> velocity;
    Particle personal_best;
};

#endif //DISSERTATION_NILM_PSO_PARTICLE_H
