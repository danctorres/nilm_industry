//
// Created by dtorres on 3/21/2023.
//

#include "PSO_Adapter.h"
#include <memory>

PSO_Adapter::PSO_Adapter(const std::vector<Particle> &particles) {
    for(const auto &par : particles){

    }
}

std::vector<Particle> PSO_Adapter::convert_to_particle() {
    std::vector<Particle> vector_particles;
    for(int i = 0; i < pso_particles.size(); i++){
        Particle part = std::make_unique<Particle>(pso_particle.get_position(), pso_particle.get_fitness());
        vector_particles(part);
    }
    return vector_particles;
}
