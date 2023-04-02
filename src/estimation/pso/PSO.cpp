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
std::vector<PSO_Particle> PSO::get_particles() const {
    return particles;
}

void PSO::initialize_velocities() {
    for (auto &particle : particles) {
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
    for (auto &particle : particles) {
        particle.set_personal_best(particle);
    }
}

void PSO::set_vmax(const float lower_bound, const float upper_bound) {
    this->v_max = (upper_bound - lower_bound) * 0.2;
}

void PSO::update_personal_best() {
    for (auto &particle : particles) {
        if (particle.get_fitness() > particle.get_personal_best().get_fitness())
            particle.set_personal_best(particle);
    }
}

// Create pso particles from particles
void PSO::adapter_particles_pso(const std::vector<Particle> &par) {
    for (int i = 0; i < n_particles; i++){
        auto pso_par = std::make_unique<PSO_Particle>(par[i]);
        particles.push_back(*pso_par);
    }
}

// Change particles, in function of the pso particles
std::vector<Particle> PSO::adapter_pso_particles(const std::vector<PSO_Particle> &pso_par) {
    std::vector<Particle> opt_particles;
    for (int i = 0; i < n_particles; i++){
        auto opt_particle = std::make_unique<Particle>(pso_par[i].get_position(), pso_par[i].get_fitness());
        opt_particles.push_back(*opt_particle);
    }
    return opt_particles;
}

PSO::PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound) : Optimization(n_particles, rank, max_iter) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    this->v_max = (upper_bound - lower_bound) * 0.2;

    // Initialize position, fitness and global bests
    std::cout << "Initializing pso population" << std::endl;
    std::vector<Particle> par = initialize_optimization(lower_bound, upper_bound);
    adapter_particles_pso(par);
    initialize_velocities();
    initialize_personal_best();

    //initialize_optimization(particles, lower_bound, upper_bound);
    auto pos_aux = particles[0].get_position();
    auto vel_aux = particles[0].get_velocity();
    auto pbest_pos_aux = particles[0].get_personal_best().get_position();

    auto gbest_pos_aux = get_global_best().get_position();

    std::cout << "DEBUG -> x: " << pos_aux[0] << " y: " << pos_aux[1] << std::endl;
    std::cout << "DEBUG -> fit: " << particles[0].get_fitness() << std::endl;
    std::cout << "DEBUG -> Vel x: " << vel_aux[0] << " Vel y: " << vel_aux[1] << std::endl;
    std::cout << "DEBUG -> Pbest x: " << pbest_pos_aux[0] << " y: " << pbest_pos_aux[1] << std::endl;
    std::cout << "DEBUG -> Pbest fit: " << particles[0].get_personal_best().get_fitness() << std::endl;
    std::cout << "DEBUG -> Gbest x: " << gbest_pos_aux[0] << " y: " << gbest_pos_aux[1] << std::endl;
    std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;



    // Initialize velocities and personal bests
    //std::cout << "Initializing velocity" << std::endl;
    //initialize_velocities();
    //std::cout << "Initializing personal best" << std::endl;
    //initialize_personal_best();

    // Initialize global best
    //std::cout << "Initializing global best" << std::endl;
    //initiate_global_best(particles);
    //std::cout << "Best position X: " << global_best.get_position()[0];
    //std::cout << "error "<< std::endl;

    //std::cout << "Best position X: " << global_best.get_position()[0] << " Pos Y: " << global_best.get_position()[1] << std::endl;
    //std::cout << "Best fitness: " << global_best.get_fitness() << std::endl;
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
            auto pb = particle.get_personal_best().get_position();   // Personal best position
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
            //calculate_set_fitness(particles);
            // Update personal_best
            //update_personal_best();
        }

        // Adapter from pso_particle to particle

        // CHANGE THIS BELLOW
        std::vector<Particle> opt_par;
        opt_par = adapter_pso_particles(particles);
        calculate_set_fitness(opt_par);
        update_global_best(opt_par);
        adapter_particles_pso(opt_par);
    }

    std::cout << "--- END ---" << std::endl;
    auto gbest_pos_aux = get_global_best().get_position();
    std::cout << "DEBUG -> Gbest x: " << gbest_pos_aux[0] << " y: " << gbest_pos_aux[1] << std::endl;
    std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;
}
