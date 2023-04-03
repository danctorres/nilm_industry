//
// Created by dtorres on 3/16/2023.
//

#ifndef DISSERTATION_NILM_OPTIMIZATION_H
#define DISSERTATION_NILM_OPTIMIZATION_H

#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include "Particle.h"


class Optimization {
public:
    Optimization();
    Optimization(int n_particles, int rank, int max_iter, std::vector<float> min_pos, std::vector<float> max_pos);
    Optimization(int n_particles, int rank, int max_iter, float min_pos, float max_pos);
    void set_n_particles(int n_particles);
    void set_rank(int rank);
    void set_max_iter(int max_iter);
    void set_min_pos(std::vector<float> min_pos);
    void set_max_pos(std::vector<float> max_pos);
    void set_global_best_parameters(const std::vector<float> &position, const float fitness);
    void set_global_best(const Particle &global_best);
    void set_particles(const std::vector<Particle> &particles);

    int get_n_particles() const;
    int get_rank() const;
    int get_max_iter() const;
    std::vector<float> get_min_pos() const;
    std::vector<float> get_max_pos() const;
    Particle get_global_best() const;
    std::vector<Particle> get_particles() const;

    // Returns fitness for positions
    float objective_function(std::vector<float> position);

    // Set the first global best for a vector of particles
    void initiate_global_best();

    // Goes through all the particles and sets the global best to the particle with the smallest fitness
    void update_global_best();

    // Initialize and return n particles with random values
    void initialize_positions();

    // Update the position of all particles with positions
    void update_positions(std::vector<Particle> &particles, const std::vector<std::vector<float>> &new_positions);

    // Update the position of all particles with positions and fitness
    void update_particles(std::vector<Particle> &particles, const std::vector<std::vector<float>> &pos, const std::vector<float> &fit);

    // Goes through all the particles, calculates the fitness and assigns to the particle
    void calculate_set_fitness();

    void initialize_optimization();

protected:
    int n_particles;                    // number of particles
    int rank;                           // rank of the polynomial function
    int max_iter;                       // max number of algorithm iterations
    std::vector<float> min_pos;
    std::vector<float> max_pos;
    Particle global_best;               // global best
    std::vector<Particle> particles;
};


#endif //DISSERTATION_NILM_OPTIMIZATION_H
