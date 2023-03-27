//
// Created by dtorres on 3/21/2023.
//

#ifndef DISSERTATION_NILM_ADAPTER_H
#define DISSERTATION_NILM_ADAPTER_H

#include "../optimization_interface/Particle.h"
#include "PSO_Particle.h"

class Adapter {
public:
    Adapter(const std::vector<PSO_Particle> &pso_particles);
    Adapter(const std::vector<Particle> &particles);
    std::vector<Particle> convert_to_particle() const;
protected:
    std::vector<PSO_Particle> pso_particles;    // Particles with the velocity and personal best
};


#endif //DISSERTATION_NILM_ADAPTER_H
