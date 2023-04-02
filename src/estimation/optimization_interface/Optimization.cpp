//
// Created by dtorres on 3/16/2023.
//
#include <algorithm>
#include <cmath>
#include <memory>
#include "Optimization.h"

Optimization::Optimization() : global_best(){
    n_particles = 0;
    rank = 0;
    max_iter = 0;
}

Optimization::Optimization(int n_particles, int rank, int max_iter) : global_best() {
    this->n_particles = n_particles;
    this->rank = rank;
    this->max_iter = max_iter;
}

void Optimization::set_n_particles(int n_particles) {
    this->n_particles = n_particles;
}

void Optimization::set_rank(int rank) {
    this->rank = rank;
}

void Optimization::set_max_iter(int max_iter) {
    this->max_iter = max_iter;
}

void Optimization::set_global_best(const Particle &global_best) {
    this->global_best.set_parameters_Particle(global_best);
}

void Optimization::set_particles(const std::vector<Particle> particles) {
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

Particle Optimization::get_global_best() const {
    return global_best;
}

std::vector<Particle> Optimization::get_particles() const {
    return particles;
}

// Returns fitness for positions
float Optimization::objective_function(std::vector<float> position){
    float fitness = 0.0;
    for(const auto &pos : position){
        fitness += pow(pos, 2);
    }
    return fitness;
}

// Set the first global best for a vector of particles
void Optimization::initiate_global_best(const std::vector<Particle> &particles) {
    set_global_best(particles.front());
    for (auto &part : particles) {
        if (part.get_fitness() < global_best.get_fitness()) {
            set_global_best(part);
        }
    }
}

// Goes through all the particles and sets the global best to the particle with the smallest fitness
void Optimization::update_global_best(const std::vector<Particle> &particles) {
    for (auto &part : particles) {
        if (part.get_fitness() < global_best.get_fitness()) {
            set_global_best(part);
        }
    }
}

// Initialize and return n particles with random values
std::vector<Particle> Optimization::initialize_positions(int min_pos, int max_pos) {
    std::vector<Particle> particles;
    for (int i = 0; i < n_particles; i++){
        std::vector<float> position;
        for (int j = 0; j < rank; j++) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(min_pos, max_pos);
            position.push_back(static_cast<float> (dis(gen)));
        }
        auto part = std::make_unique<Particle>(position);
        particles.push_back(*part);
    }
    return particles;
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
void Optimization::calculate_set_fitness(std::vector<Particle> &particles) {
    std::for_each(particles.begin(), particles.end(), [this](Particle &par) {
        par.set_fitness(objective_function(par.get_position()));
    });
}

std::vector<Particle> Optimization::initialize_optimization(int min_pos, int max_pos) {
    std::cout << "Initializing population" << std::endl;
    std::vector<Particle> particles = initialize_positions(min_pos, max_pos);
    std::cout << "Initializing fitness" << std::endl;
    calculate_set_fitness(particles);
    std::cout << "Initializing global best" << std::endl;
    initiate_global_best(particles);
    return particles;
}
