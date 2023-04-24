//
// Created by danctorres on 3/11/23.
//

#include "PSO.h"


std::vector<PSO_Particle> PSO::get_particles() const {
    return pso_particles;
}

void PSO::initialize_velocities() {
    std::vector<float> velocity;
    for (PSO_Particle &pso_particle : pso_particles) {
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(-v_max[j], v_max[j]);
            velocity.push_back(static_cast<float> (dis(gen)));
        }
        pso_particle.set_velocity(velocity);
        velocity.clear();
    }
}

void PSO::initialize_personal_best() {
    for (PSO_Particle &particle : pso_particles) {
        particle.set_personal_best(particle);
    }
}

void PSO::set_v_max(const std::vector<float> &pos_min, const std::vector<float> &pos_max) {
    for (int i = 0; i < rank; i++) {
        this->v_max.push_back((pos_max[i] - pos_min[i]) * 0.2);
    }
}

void PSO::update_personal_best() {
    for (PSO_Particle &particle : pso_particles) {
        if (particle.get_fitness() > particle.get_personal_best().get_fitness())
            particle.set_personal_best(particle);
    }
}

// Create pso particles from particles
void PSO::adapter_particles_pso() {
    for (auto &particle : particles) {
        PSO_Particle pso_par = PSO_Particle(particle);
        pso_particles.push_back(pso_par);
    }
}

// Change particles, in function of the pso particles
void PSO::adapter_pso_particles() {
    for (int i = 0; i < n_particles; i++) {
        particles[i].set_position(pso_particles[i].get_position());
        particles[i].set_fitness(pso_particles[i].get_fitness());
    }
}

PSO::PSO(int n_particles, int rank, int max_iter, std::vector<float> &min_pos, std::vector<float> &max_pos, float c1,
         float c2, float w_min, float w_max) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    for (int i = 0; i < rank; i++) {
        this->v_max.push_back((max_pos[i] - min_pos[i]) * 0.2);
    }

    // Initialize position, fitness and global bests
    std::cout << "- Number of particles: " << n_particles << ", ";
    std::cout << "c1: " << c1 << ", ";
    std::cout << "c2: " << c1 << ", ";
    std::cout << "w_min: " << w_min << ", ";
    std::cout << "w_max: " << w_max << " - " << std::endl;

    initialize_optimization();
    adapter_particles_pso();

    initialize_velocities();
    initialize_personal_best();
}

void PSO::run() {
    // Main PSO loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.1);
    float w = 1.0f;

    float stop_condition = global_best.get_fitness();
    int stopping_counter = 0;

    for(int i = 0; i < max_iter; i++){
        w = w_max - i * ((w_max - w_min) / max_iter);

        std::vector<float> new_velocity;
        std::vector<float> new_position;
        for(PSO_Particle &pso_particle : pso_particles) {
            // Update particle position and velocity
            auto pos = pso_particle.get_position();             // Particles position
            auto vel = pso_particle.get_velocity();             // Particles velocity
            auto pb = pso_particle.get_personal_best().get_position();   // Personal best position
            auto gb = global_best.get_position();

            float r1 = dis(gen);
            float r2 = dis(gen);

            float nv = 0.0f;
            float np = 0.0f;
            for (int k = 0; k < rank; k++){
                nv = w * vel[k] + c1 * r1 * (pb[k] - pos[k]) + c2 * r2 * (gb[k] - pos[k]);

                if (nv < v_max[k] || nv > -v_max[k]){
                    np = pos[k] + nv;
                    new_velocity.push_back(nv);
                    new_position.push_back(np);
                }
            }
            pso_particle.set_velocity(new_velocity);
            pso_particle.set_position(new_position);

            new_position.clear();
            new_velocity.clear();
        }

        adapter_pso_particles();
        calculate_set_fitness();
        update_global_best();

        // Stopping conditions
        if (get_global_best().get_fitness() < 0.001){
            return;
        }
        else {
            if (stop_condition == get_global_best().get_fitness()) {
                if (stopping_counter >= 2 && get_global_best().get_fitness() < 0.01) {
                    std::cout << "- Number of cycles " << i << " - " << std::endl;
                    return;
                }
                stopping_counter++;
            } else {
                stopping_counter = 0;
                stop_condition = global_best.get_fitness();
            }
        }
    }
}
