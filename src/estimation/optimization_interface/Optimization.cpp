//
// Created by danctorres on 3/16/2023.
//

#include "Optimization.h"


Optimization::Optimization() : global_best(){
    n_particles = 0;
    rank = 0;
    max_iter = 0;
    min_pos.push_back(0.0f);
    max_pos.push_back(0.0f);
}

Optimization::Optimization(int n_particles, int rank, int max_iter, float min_pos, float max_pos) : global_best() {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
    this->min_pos.push_back(min_pos);
    this->max_pos.push_back(max_pos);
}

Optimization::Optimization(const int n_particles, const int rank, const int max_iter, const std::vector<float> &min_pos,
                           const std::vector<float> &max_pos) : global_best() {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
    this->min_pos = min_pos;
    this->max_pos = max_pos;
}

Optimization::Optimization(const int n_particles, const int rank, const int max_iter, const std::vector<float> &min_pos,
                           const std::vector<float> &max_pos, const std::vector<Particle> &particles)  : global_best() {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
    this->min_pos = min_pos;
    this->max_pos = max_pos;
    this->particles = particles;
}

void Optimization::set_n_particles(const int n_particles) {
    this->n_particles = n_particles;
}

void Optimization::set_rank(const int rank) {
    this->rank = rank;
}

void Optimization::set_max_iter(const int max_iter) {
    this->max_iter = max_iter;
}

void Optimization::set_min_pos(const std::vector<float> &min_pos) {
    this->min_pos = min_pos;
}

void Optimization::set_max_pos(const std::vector<float> &max_pos) {
    this->max_pos = max_pos;
}

void Optimization::set_global_best(const Particle &global_best) {
    this->global_best.set_parameters_Particle(global_best);
}

void Optimization::set_particles(const std::vector<Particle> &particles) {
    this->particles = particles;
}

int Optimization::get_n_particles() const{
    return n_particles;
}

int Optimization::get_rank() const {
    return rank;
}

int Optimization::get_max_iter() const {
    return max_iter;
}

std::vector<float> Optimization::get_min_pos() const {
    return min_pos;
}

std::vector<float> Optimization::get_max_pos() const {
    return max_pos;
}

Particle Optimization::get_global_best() const {
    return global_best;
}

std::vector<Particle> Optimization::get_particles() const {
    return particles;
}

// Returns fitness for positions
float Optimization::objective_function(const std::vector<float> &position){
    return pow(position[0] + 3, 2) + sqrt(pow(position[1], 2));
}

// Set the first global best for a vector of particles
void Optimization::initialize_global_best() {
    set_global_best(particles.front());
    for (auto &part : particles) {
        if (part.get_fitness() < global_best.get_fitness()) {
            set_global_best(part);
        }
    }
}

// Goes through all the particles and sets the global best to the particle with the smallest fitness
void Optimization::update_global_best() {
    for (auto &part : particles) {
        if (part.get_fitness() < global_best.get_fitness()) {
            set_global_best(part);
        }
    }
}

// Initialize and return n particles with random values
void Optimization::initialize_positions() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::vector<float> position;
    for (int i = 0; i < n_particles; i++){
        for (int j = 0; j < rank; j++) {
            std::uniform_real_distribution<> dis(min_pos[j], max_pos[j]);
            position.push_back(static_cast<float> (dis(gen)));
        }
        Particle part = Particle(position);
        particles.push_back(part);
        position.clear();
    }
}

void Optimization::initialize_positions(std::vector<Particle> &particles) {
    for (Particle &particle : particles){
        std::vector<float> position;
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(min_pos[j], max_pos[j]);
            position.push_back(static_cast<float> (dis(gen)));
        }
        particle.set_position(position);
    }
}

// Update the position of all particles with positions
void Optimization::update_positions(std::vector<Particle> &particles, const std::vector<std::vector<float>> &new_positions) {
    for (int i = 0; i < n_particles ; i++){
        particles[i].set_position(new_positions[i]);
    }
}

// Update the position of all particles with positions and fitness
void Optimization::update_particles(std::vector<Particle> &particles, const std::vector<std::vector<float>> &pos,
                                    const std::vector<float> &fit) {
    for (int i = 0; i < n_particles ; i++){
        particles[i].set_position(pos[i]);
        particles[i].set_fitness(fit[i]);
    }
}

// Goes through all the particles, calculates the fitness and assigns to the particle
void Optimization::calculate_set_fitness() {
    std::for_each(particles.begin(), particles.end(), [this](Particle &par) {
        par.set_fitness(objective_function(par.get_position()));
    });
}

void Optimization::calculate_set_fitness(std::vector<Particle> &particles) {
    for (Particle &particle : particles) {
        particle.set_fitness(objective_function(particle.get_position()));
    }
}

void Optimization::sort_particles() {
    std::sort(particles.begin(), particles.end(), [](const Particle& par1, const Particle& par2) {
        return par1.get_fitness() < par2.get_fitness();
    });
}

void Optimization::initialize_optimization() {
    //std::cout << "Initializing population" << std::endl;
    initialize_positions();
    //std::cout << "Initializing fitness" << std::endl;
    calculate_set_fitness();
    //std::cout << "Initializing global best" << std::endl;
    initialize_global_best();
}

void Optimization::initialize_optimization(std::vector<Particle> &particles) {
    initialize_positions(particles);
    calculate_set_fitness();
    initialize_global_best();
}
