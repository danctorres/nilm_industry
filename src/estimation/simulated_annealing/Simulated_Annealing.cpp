//
// Created by danie on 3/16/2023.
//

#include "Simulated_Annealing.h"

void Simulated_Annealing::set_temperature(float temperature) {
    this->temperature = temperature;
}

float Simulated_Annealing::get_temperature() const {
    return temperature;
}

Simulated_Annealing::Simulated_Annealing(int n_particles, int rank, int max_iter) : Optimization(n_particles, rank, max_iter, lower_bound, upper_bound) {
    std::cout << "Initializing simulated annealing population" << std::endl;
    initialize_optimization();
    adapter_particles_pso();
    set_particles(particles);
}

void Simulated_Annealing::run() {
    // Main loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0, 1);
    float w = 1.0;

    float stop_condition = global_best.get_fitness();
    int stopping_counter = 0;

    for (int i = 0; i < max_iter; i++) {
        w = w_max - i * ((w_max - w_min) / max_iter);

        std::vector<float> new_velocity;
        std::vector<float> new_position;
        for (PSO_Particle &particle: pso_particles) {
        }
    }
}
