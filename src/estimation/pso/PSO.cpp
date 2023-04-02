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

PSO::PSO(int n_particles, int rank, int max_iter, float c1, float c2, float w_min, float w_max, float lower_bound, float upper_bound) : Optimization(n_particles, rank, max_iter) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    this->v_max = (upper_bound - lower_bound) * 0.2;

    // Initialize position, fitness and global bests
    std::cout << "Initializing pso population" << std::endl;
    initialize_optimization(lower_bound, upper_bound);
    adapter_particles_pso();
    set_particles(particles);

    initialize_velocities();
    initialize_personal_best();

    //initialize_optimization(particles, lower_bound, upper_bound);
    auto pos_aux = pso_particles[0].get_position();
    auto vel_aux = pso_particles[0].get_velocity();
    auto pbest_pos_aux = pso_particles[0].get_personal_best().get_position();

    auto gbest_pos_aux = get_global_best().get_position();

    std::cout << "DEBUG -> x: " << pos_aux[0] << " y: " << pos_aux[1] << std::endl;
    std::cout << "DEBUG -> fit: " << pso_particles[0].get_fitness() << std::endl;
    std::cout << "DEBUG -> Vel x: " << vel_aux[0] << " Vel y: " << vel_aux[1] << std::endl;
    std::cout << "DEBUG -> Pbest x: " << pbest_pos_aux[0] << " y: " << pbest_pos_aux[1] << std::endl;
    std::cout << "DEBUG -> Pbest fit: " << pso_particles[0].get_personal_best().get_fitness() << std::endl;
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

    float stop_condition = global_best.get_fitness();
    int stoping_counter = 0;

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
                /*if(nv > v_max || nv < -v_max) {
                    nv = v_max;
                }*/

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


        //auto pos_aux = pso_particles[0].get_position();
        auto vel_aux = pso_particles[0].get_velocity();
        //auto pbest_pos_aux = pso_particles[0].get_personal_best().get_position();
        //auto gbest_pos_aux = get_global_best().get_position();
        /*std::cout << "DEBUG -> x: " << pos_aux[0] << " y: " << pos_aux[1] << std::endl;
        std::cout << "DEBUG -> fit: " << pso_particles[0].get_fitness() << std::endl;*/
        std::cout << "DEBUG -> Vel x: " << vel_aux[0] << " Vel y: " << vel_aux[1] << std::endl;
        /*std::cout << "DEBUG -> Pbest x: " << pbest_pos_aux[0] << " y: " << pbest_pos_aux[1] << std::endl;
        std::cout << "DEBUG -> Pbest fit: " << pso_particles[0].get_personal_best().get_fitness() << std::endl;
        std::cout << "DEBUG -> Gbest x: " << gbest_pos_aux[0] << " y: " << gbest_pos_aux[1] << std::endl;
        std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;*/

        if(stop_condition == get_global_best().get_fitness()) {
            if (stoping_counter == 10 || get_global_best().get_fitness() < 0.001) {
                std::cout << "--- Number of cycles " << i << " --- " << std::endl;
                break;
            }
            std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;
            stoping_counter++;
        }
        else {
            stop_condition = global_best.get_fitness();
        }
    }

    std::cout << "--- END ---" << std::endl;
    auto gbest_pos_aux = get_global_best().get_position();
    std::cout << "DEBUG -> Gbest x: " << gbest_pos_aux[0] << " y: " << gbest_pos_aux[1] << std::endl;
    std::cout << "DEBUG -> Gbest fit: " << get_global_best().get_fitness() << std::endl;
}
