//
// Created by dtorres on 3/11/23.
//

#include "PSO.h"
#include <cmath>
#include <iostream>
#include <cstdlib>
#include <ctime>
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
void PSO::objective_function() {
    int fitness = 0;
    for (int i = 0; i < particles.size(); i++) {
        PSO_Particle particle = particles[i];
        std::vector<int> pos = particle.get_position();
        for (int j = 0; j < pos.size(); j++) {
            fitness += pow(pos[j], 2);
        }
        particle.set_fitness(fitness);
    }
}

void PSO::set_global_best() {
    for (int i = 0; i < particles.size(); i++){
        if(global_best.get_fitness() > particles[i].get_fitness()){
            global_best.set_position(particles[i].get_position());
            global_best.set_fitness(particles[i].get_fitness());
        }
    }
}

PSO::PSO(int rank, int n_particles, int max_iter, int c1, int c2, int w_min, int w_max, int v_max) {
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
        srand(time(0));

        std::vector<int> position;
        std::vector<int> velocity;
        for (int j = 0; j < rank; j++){
            position.push_back(rand() % 10);
            velocity.push_back(0);
        }

        // Set particles
        PSO_Particle particle(position, velocity, 0);
        particles.push_back(particle);

        // Calculate fitness
        objective_function();
    }

    // Calculate and set global_best
    global_best = PSO_Best_Particle();
    set_global_best();

    std::cout << "Best position x: " << global_best.get_position()[0] << " Pos Y: " << global_best.get_position()[1] << std::endl;
    std::cout << "Best fitness: " << global_best.get_fitness() << std::endl;
}

std::vector<PSO_Particle> PSO::get_particles() const {
    return particles;
}

PSO_Best_Particle PSO::get_global_best() const{
    return global_best;
}