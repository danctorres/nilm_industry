//
// Created by dtorres on 3/11/23.
//

#include "PSO.h"
#include <cmath>
#include <iostream>
#include <random>
#include <cstdlib>
#include "PSO_Particle.h"
#include "PSO_Particle.cpp"

/*
int PSO::objective_function(Read_Aggregate &data, Read_State &states){
    // Define objective function: || X - WH|| ^ 2
    //std::vector<uint32_t> active_power = data.get_parameter("Active power");
    //states.get_all_parameter();
}
 */

// Testing PSO
float PSO::objective_function(std::vector<float> position){
    float fitness = 0.0;
    for (int j = 0; j < position.size(); j++) {
        fitness += pow(position[j], 2);
    }
    return fitness;
}

void PSO::set_global_best() {
    global_best.set_position(particles[0].get_position());
    global_best.set_fitness(particles[0].get_fitness());
    for (int i = 0; i < particles.size(); i++){
        if(particles[i].get_fitness() < global_best.get_fitness()){
            global_best.set_position(particles[i].get_position());
            global_best.set_fitness(particles[i].get_fitness());
        }
    }
}

void PSO::update_global_best() {
    for (int i = 0; i < particles.size(); i++){
        if(particles[i].get_fitness() < global_best.get_fitness()){
            global_best.set_position(particles[i].get_position());
            global_best.set_fitness(particles[i].get_fitness());
        }
    }
}

PSO::PSO(int rank, int n_particles, int max_iter, float c1, float c2, float w_min, float w_max, float v_max) {
    // Set PSO constants
    this->rank = rank;
    this->n_particles = n_particles;
    this->max_iter = max_iter;
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    this->v_max = v_max;

    // Initialize population of N particles
    std::cout << "Initializing PSO population" << std::endl;
    for (int i = 0; i < n_particles; i++){
        std::vector<float> position;
        std::vector<float> velocity;
        for (int j = 0; j < rank; j++){
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(0, 10);
            position.push_back(dis(gen));
            velocity.push_back(0);
        }

        // Calculate fitness
        float fitness = objective_function(position);

        // Set particles
        PSO_Particle particle(position, velocity, fitness);
        particles.push_back(particle);

        // Set personal_best
        particle.set_best();
    }

    // Calculate and set global_best
    global_best = PSO_Best_Particle();
    set_global_best();

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
    // Main PSO loop

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0, 1);
    float w = 1.0;
    for(int i = 0; i < max_iter; i++){
         //w = w_max - i * ((w_max - w_min) / w_min);
        //std::cout << "w: " << w << std::endl;

        for(int j = 0; j < n_particles ; j++){
            // Update particle position and velocity
            auto p = particles[j].get_position();               // Particles position
            auto v = particles[j].get_velocity();               // Particles velocity
            auto pb = particles[j].get_best().get_position();   // Personal best position
            auto gb = global_best.get_position();

            float r1 = dis(gen);
            float r2 = dis(gen);
            std::vector<float> new_velocity;
            std::vector<float> new_position;
            for (int k = 0; k < rank; k++){
                float nv = w * v[k] + c1 * r1 * (pb[k] - p[k]) + c2 * r2 * (gb[k] - p[k]);
                float np = p[k] + nv;
                new_velocity.push_back(nv);
                new_position.push_back(np);
            }
            particles[j].set_velocity(new_velocity);
            particles[j].set_position(new_position);

            //std::cout << "New position: " << particles[j].get_position()[0] << " " << particles[j].get_position()[1] << std::endl;

            // Calculate fitness
            particles[j].set_fitness(objective_function(new_position));
            // Update personal_best
            particles[j].update_pbest();
        }

        // Update pbest and gbest
        update_global_best();
    }
}
