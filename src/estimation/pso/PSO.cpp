//
// Created by dtorres on 3/11/23.
//
#include <cmath>
#include <iostream>
#include <random>
#include "PSO.h"

/*
int pso::objective_function(Read_Aggregate &data, Read_State &states){
    // Define objective function: || X - WH|| ^ 2
    //std::vector<uint32_t> active_power = data.get_parameter("Active power");
    //states.get_all_parameter();
}
 */

void PSO::set_velocities() {
    for (int i = 0; i < get_n_particles(); i++) {
        std::vector<float> velocity;
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(min_vel, max_vel);
            velocity.push_back(static_cast<float> (dis(gen)));
        }
        auto pso_part = std::make_unique<PSO_Particle>(velocity);
        pso_particles.push_back(*pso_part);
    }
}

void PSO::set_vmax(const float lower_bound, const float upper_bound) {
    this->v_max = (upper_bound - lower_bound) * 0.2;
}

PSO::PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound) : Optimization(n_particles, rank, max_iter) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    this->v_max = (upper_bound - lower_bound) * 0.2;

    // Initialize population of N particles
    std::cout << "Initializing pso population" << std::endl;
    // Set the  initial particles position
    set_positions(0, 10);   // change!!!
    // Set the fitness for the particles
    calculate_set_fitness();
    // Set global best
    calculate_set_global_best();

    // Set PSO particles
    // Set velocities
    set_velocities();
    // Set personal best
    update_best();

    // Set max velocity
    set_vmax(lower_bound, upper_bound);

        // Set particles
        PSO_Particle particle(position, velocity, fitness);
        particles.push_back(particle);

        // Set personal_best
        particle.set_best();
    }

    // Calculate and set global_best
    global_best = PSO_Best_Particle();
    global_best.set_position(particles[0].get_position());
    global_best.set_fitness(particles[0].get_fitness());
    update_global_best();

    std::cout << "Best position X: " << global_best.get_position()[0] << " Pos Y: " << global_best.get_position()[1] << std::endl;
    std::cout << "Best fitness: " << global_best.get_fitness() << std::endl;
}

std::vector<PSO_Particle> PSO::get_particles() const {
    return particles;
}

PSO_Best_Particle PSO::get_global_best() const{
    return global_best;
}

void PSO::run_pso() {
    // Main pso loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0, 1);
    float w = 1.0;
    for(int i = 0; i < max_iter; i++){
        //w = w_max - i * ((w_max - w_min) / w_min);

        for(auto &particle : particles){
            //std::cout << "w: " << w << std::endl;
            // Update particle position and velocity
            auto pos = particle.get_position();             // Particles position
            auto vel = particle.get_velocity();             // Particles velocity
            auto pb = particle.get_best().get_position();   // Personal best position
            auto gb = global_best.get_position();

            float r1 = dis(gen);
            float r2 = dis(gen);
            std::vector<float> new_velocity;
            std::vector<float> new_position;
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

            //std::cout << "New position: " << part.get_position()[0] << " " << part.get_position()[1] << std::endl;

            // Calculate fitness
            particle.set_fitness(objective_function(new_position));
            // Update personal_best
            particle.update_pbest();
        }

        // Update pbest and gbest
        update_global_best();
    }
}
