//
// Created by dtorres on 3/11/23.
//
#include <cmath>
#include <iostream>
#include <random>
#include "PSO.h"


std::vector<PSO_Particle> PSO::get_particles() const {
    return pso_particles;
}

void PSO::initialize_velocities() {
    for (PSO_Particle &particle : pso_particles) {
        std::vector<float> velocity;
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(-v_max, v_max);
            velocity.push_back(static_cast<float> (dis(gen)));
        }
        particle.set_velocity(velocity);
    }
}

void PSO::initialize_personal_best() {
    for (PSO_Particle &particle : pso_particles) {
        particle.set_personal_best(particle);
    }
}

void PSO::set_vmax(const float lower_bound, const float upper_bound) {
    this->v_max = (upper_bound - lower_bound) * 0.2;
}

void PSO::update_personal_best() {
    for (PSO_Particle &particle : pso_particles) {
        if (particle.get_fitness() > particle.get_personal_best().get_fitness())
            particle.set_personal_best(particle);
    }
}

// Create pso particles from particles
void PSO::adapter_particles_pso() {
    for (auto &particle : particles){
        PSO_Particle pso_par = PSO_Particle(particle);
        pso_particles.push_back(pso_par);
    }
}

// Change particles, in function of the pso particles
void PSO::adapter_pso_particles() {
    for (int i = 0; i < n_particles; i++){
        particles[i].set_position(pso_particles[i].get_position());
        particles[i].set_fitness(pso_particles[i].get_fitness());
    }
}

PSO::PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, int lower_bound, int upper_bound) : Optimization(n_particles, rank, max_iter, lower_bound, upper_bound) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    this->v_max = (upper_bound - lower_bound) * 0.2;

    // Initialize position, fitness and global bests
    std::cout << "Initializing pso population" << std::endl;
    initialize_optimization();
    adapter_particles_pso();

    initialize_velocities();
    initialize_personal_best();
}

void PSO::run() {
    // Main PSO loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0, 1);
    float w = 1.0;

    float stop_condition = global_best.get_fitness();
    int stopping_counter = 0;

    for(int i = 0; i < max_iter; i++){
        w = w_max - i * ((w_max - w_min) / max_iter);

        std::vector<float> new_velocity;
        std::vector<float> new_position;
        for(PSO_Particle &particle : pso_particles){
            // Update particle position and velocity
            auto pos = particle.get_position();             // Particles position
            auto vel = particle.get_velocity();             // Particles velocity
            auto pb = particle.get_personal_best().get_position();   // Personal best position
            auto gb = global_best.get_position();

            float r1 = dis(gen);
            float r2 = dis(gen);

            float nv = 0.0;
            float np = 0.0;
            for (int k = 0; k < rank; k++){
                nv = w * vel[k] + c1 * r1 * (pb[k] - pos[k]) + c2 * r2 * (gb[k] - pos[k]);

                if (nv < v_max || nv > -v_max){
                    np = pos[k] + nv;
                    new_velocity.push_back(nv);
                    new_position.push_back(np);
                }
            }
            particle.set_velocity(new_velocity);
            particle.set_position(new_position);

            new_position.clear();
            new_velocity.clear();
        }

        adapter_pso_particles();
        calculate_set_fitness();
        update_global_best();

        // Stopping conditions
        if(stop_condition == get_global_best().get_fitness()) {
            if (stopping_counter == 10 || get_global_best().get_fitness() < 0.001) {
                std::cout << "--- Number of cycles " << i << " --- " << std::endl;
                break;
            }
            std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;
            stopping_counter++;
        }
        else {
            stop_condition = global_best.get_fitness();
        }
    }
}
