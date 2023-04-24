//
// Created by danctorres on 3/16/2023.
//

#include "Simulated_Annealing.h"
#include "../optimization_interface/Particle.h"


void Simulated_Annealing::set_temperature(float temperature) {
    this->temperature = temperature;
}

void Simulated_Annealing::set_temp_min(float temp_min) {
    this->temp_min = temp_min;
}

void Simulated_Annealing::set_cooling_factor(float cooling_factor) {
    this->cooling_factor = cooling_factor;
}

void Simulated_Annealing::set_last_fitness() {
    for (Particle &particle : particles) {
        last_fitness.push_back(particle.get_fitness());
    }
}

float Simulated_Annealing::get_temperature() const {
    return temperature;
}

float Simulated_Annealing::get_temp_min() const {
    return temp_min;
}

float Simulated_Annealing::get_cooling_factor() const {
    return cooling_factor;
}


std::vector<float> Simulated_Annealing::get_last_fitness() const {
    return last_fitness;
}

float Simulated_Annealing::calculate_new_fitness(const std::vector<float> &new_positions) {
    return objective_function(new_positions);
}

float Simulated_Annealing::calculate_delta(const Particle &particle, float fitness) {
    return particle.get_fitness() - fitness;
}

Simulated_Annealing::Simulated_Annealing(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float temperature, float temp_min, float cooling_factor) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    // Initializing member variables
    this->temperature = temperature;
    this->temp_min = temp_min;
    this->cooling_factor = cooling_factor;

    //std::cout << "Initializing simulated annealing population" << std::endl;
    std::cout << "- Number of particles: " << n_particles << ", ";
    std::cout << "temperature: " << temperature << ", ";
    std::cout << "temp_min: " << temp_min << ", ";
    std::cout << "cooling_factor: " << cooling_factor << " - " << std::endl;

    initialize_optimization();
    set_last_fitness();
}

void Simulated_Annealing::run() {
    // Main loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis1(-0.5, 0.5);
    std::uniform_real_distribution<> dis2(0, 1);

    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        std::vector<float> new_position;
        float new_fitness = 0.0f;
        float delta = 0.0f;
        float cond = 0.0f;
        for (Particle &particle: particles) {
            for (int j = 0; j < rank; j++) {
                new_position.push_back(particle.get_position()[j] + dis1(gen));
            }
            new_fitness = calculate_new_fitness(new_position);
            delta = calculate_delta(particle, new_fitness);

            // new position has smaller fitness
            if (delta < 0.0){
                particle.set_position(new_position);
                particle.set_fitness(new_fitness);
            }
            else{
                if (exp(-delta / temperature) > dis2(gen)){
                    particle.set_position(new_position);
                    particle.set_fitness(new_fitness);
                }
            }
            new_position.clear();
        }
        update_global_best();

        //update_global_best();
        //std::cout << "GB fit: " << global_best.get_fitness() << std::endl;
        //std::cout << "GB pos x: " << global_best.get_position()[0] << " y: " << global_best.get_position()[1] << std::endl;


        temperature *= cooling_factor;

        if (temperature < temp_min){
            return;
        }
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
