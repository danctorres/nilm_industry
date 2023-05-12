//
// Created by danctorres on 3/11/23.
//

#include "PSO.h"


void PSO::set_c1(const float c1) {
    this->c1 = c1;
}

void PSO::set_c2(const float c2) {
    this->c2 = c2;
}

void PSO::set_w_min(const float w_min) {
    this->w_min = w_min;
}

void PSO::set_w_max(const float w_max) {
    this->w_max = w_max;
}

void PSO::set_v_max(const std::vector<double> &v_max) {
    this->v_max = v_max;
}

void PSO::set_v_max(const std::vector<double> &pos_min, const std::vector<double> &pos_max) {
    for (int i = 0; i < rank; i++) {
        this->v_max.push_back((pos_max[i] - pos_min[i]) * 0.2);
    }
}

void PSO::set_pso_particles(const std::vector<PSO_Particle> &pso_particles) {
    this->pso_particles = pso_particles;
}

float PSO::get_c1() const {
    return c1;
}

float PSO::get_c2() const {
    return c2;
}

float PSO::get_w_min() const {
    return w_min;
}

float PSO::get_w_max() const {
    return w_max;
}

std::vector<double> PSO::get_v_max() const {
    return v_max;
}

std::vector<PSO_Particle> PSO::get_pso_particles() const {
    return pso_particles;
}

void PSO::initialize_velocities() {
    std::vector<double> velocity;
    for (PSO_Particle &pso_particle : pso_particles) {
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(-v_max[j], v_max[j]);
            velocity.push_back(static_cast<double> (dis(gen)));
        }
        pso_particle.set_velocity(velocity);
        velocity.clear();
    }
}

void PSO::initialize_personal_best() {
    for (PSO_Particle &pso_particle : pso_particles) {
        pso_particle.set_personal_best(pso_particle);
    }
}

void PSO::update_personal_best() {
    for (PSO_Particle &pso_particle : pso_particles) {
        if (pso_particle.get_fitness() > pso_particle.get_personal_best().get_fitness())
            pso_particle.set_personal_best(pso_particle);
    }
}

// Create pso particles from particles
void PSO::adapter_particles_pso() {
    for (const auto &particle : particles) {
        PSO_Particle pso_par = PSO_Particle(particle);
        pso_particles.push_back(pso_par);
    }
}

// Change particles, in polynomial_function of the pso particles
void PSO::adapter_pso_particles() {
    for (int i = 0; i < pso_particles.size(); i++) {
        particles[i].set_position(pso_particles[i].get_position());
        //particles[i].set_fitness(pso_particles[i].get_fitness());
    }
}

PSO::PSO(const int n_particles, const int rank, const int max_iter, const float threshold,
         const std::vector<float> &min_pos, const std::vector<float> &max_pos, const float c1, const float c2,
         const float w_min, const float w_max) : Optimization(n_particles, rank, max_iter, threshold, min_pos, max_pos) {
    // Set pso constants
    this->c1 = c1;
    this->c2 = c2;
    this->w_min = w_min;
    this->w_max = w_max;
    for (int i = 0; i < rank; i++) {
        this->v_max.push_back((max_pos[i] - min_pos[i]) * 0.2);
    }

    initialize_optimization();
    adapter_particles_pso();

    initialize_velocities();
    initialize_personal_best();

    /*std::cout << "- Number of particles = " << n_particles << ", ";
    std::cout << "c1 = " << c1 << ", ";
    std::cout << "c2 = " << c1 << ", ";
    std::cout << "w_min = " << w_min << ", ";
    std::cout << "w_max = " << w_max << std::endl;*/

}

void PSO::run() {
    // Main PSO loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 2.0);
    float w = 1.0f;

    float stop_condition = global_best.get_fitness();
    int stopping_counter = 0;

    for(int i = 0; i < max_iter; i++){
        w = w_max - i * ((w_max - w_min) / max_iter);

        std::vector<double> new_velocity;
        std::vector<double> new_position;
        for(PSO_Particle &pso_particle : pso_particles) {
            // Update particle position and velocity
            auto pos = pso_particle.get_position();             // Particles position
            auto vel = pso_particle.get_velocity();             // Particles velocity
            auto pb = pso_particle.get_personal_best().get_position();   // Personal best position
            auto gb = global_best.get_position();

            double r1 = dis(gen);
            double r2 = dis(gen);

            double nv = 0.0;
            double np = 0.0;
            for (int k = 0; k < rank; k++){
                nv = w * vel[k] + c1 * r1 * (pb[k] - pos[k]) + c2 * r2 * (gb[k] - pos[k]);

                if (nv > v_max[k]) {
                    nv = v_max[k];
                }
                else if(nv < -v_max[k]) {
                    nv = -v_max[k];
                }
                np = pos[k] + nv;
                new_velocity.push_back(nv);
                new_position.push_back(np);
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
        if (stopping_condition(global_best.get_fitness(), stopping_counter, stop_condition, i)) {
            return;
        }
    }
    // std::cout << "- Number of cycles " << max_iter << " - " << std::endl;
}
