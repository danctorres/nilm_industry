//
// Created by danctorres on 3/16/2023.
//

#include "SA.h"
#include "../optimization_interface/Particle.h"


void SA::set_temperature(float temperature) {
    this->temperature = temperature;
}

void SA::set_temp_min(float temp_min) {
    this->temp_min = temp_min;
}

void SA::set_cooling_factor(float cooling_factor) {
    this->cooling_factor = cooling_factor;
}

void SA::set_last_fitness() {
    for (Particle &particle : particles) {
        last_fitness.push_back(particle.get_fitness());
    }
}

float SA::get_temperature() const {
    return temperature;
}

float SA::get_temp_min() const {
    return temp_min;
}

float SA::get_cooling_factor() const {
    return cooling_factor;
}


std::vector<float> SA::get_last_fitness() const {
    return last_fitness;
}

float SA::calculate_new_fitness(const std::vector<float> &new_positions) {
    return objective_function(new_positions);
}


SA::SA(const int n_particles, const int rank, const int max_iter, const float threshold,
const std::vector<float> &min_pos, const std::vector<float> &max_pos,
const float temperature, const float temp_min, const float cooling_factor) : Optimization(n_particles, rank, max_iter, threshold, min_pos, max_pos) {
    // Initializing member variables
    this->temperature = temperature;
    this->temp_min = temp_min;
    this->cooling_factor = cooling_factor;

    //std::cout << "Initializing simulated annealing population" << std::endl;
    std::cout << "- Number of particles = " << n_particles << ", ";
    std::cout << "temperature = " << temperature << ", ";
    std::cout << "temp_min = " << temp_min << ", ";
    std::cout << "cooling_factor = " << cooling_factor << " - " << std::endl;

    initialize_optimization();
    set_last_fitness();
}

void SA::run() {
    // Main loop
    std::random_device rd;
    std::mt19937 gen(rd());
    // Values need to be tuned in to the specific problem
    std::uniform_real_distribution<> dis1(-0.2f, 0.2f);
    std::uniform_real_distribution<> dis2(0.0f, 0.2f);

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
            delta = particle.get_fitness() - new_fitness;

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
            new_fitness = 0.0f;
        }
        update_global_best();

        //update_global_best();
        //std::cout << "GB fit: " << global_best.get_fitness() << std::endl;
        //std::cout << "GB pos x: " << global_best.get_position()[0] << " y: " << global_best.get_position()[1] << std::endl;

        set_temperature(temperature * cooling_factor);

        if (temperature < temp_min){
            return;
        }

        if (stopping_condition(global_best.get_fitness(), stopping_counter, stop_condition, i)) {
            return;
        }
    }
    std::cout << "- Number of cycles " << max_iter << " - " << std::endl;
}
