//
// Created by danctorres on 3/16/2023.
//

#ifndef DISSERTATION_NILM_OPTIMIZATION_H
#define DISSERTATION_NILM_OPTIMIZATION_H

#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include "Particle.h"
#include "../problem_formulation/objective_function.h"


class Optimization {
public:
    Optimization();
    Optimization(const int n_particles, const int rank, const int max_iter, const float threshold,
                 const std::vector<float> &min_pos, const std::vector<float> &max_pos);
    Optimization(const int n_particles, const int rank, const int max_iter, const float threshold,
                 const std::vector<float> &min_pos, const std::vector<float> &max_pos, const std::vector<Particle> &particles);
    Optimization(const int n_particles, const int rank, const int max_iter, const float threshold, const float min_pos, const float max_pos);
    void set_n_particles(const int n_particles);
    void set_rank(const int rank);
    void set_max_iter(const int max_iter);
    void set_threshold(const float threshold);
    void set_min_pos(const std::vector<float> &min_pos);
    void set_max_pos(const std::vector<float> &max_pos);
    void set_global_best_parameters(const std::vector<float> &position, const double fitness);
    void set_global_best(const Particle &global_best);
    void set_particles(const std::vector<Particle> &particles);

    int get_n_particles() const;
    int get_rank() const;
    int get_max_iter() const;
    float get_threshold() const;
    std::vector<float> get_min_pos() const;
    std::vector<float> get_max_pos() const;
    Particle get_global_best() const;
    std::vector<Particle> get_particles() const;

    // Returns fitness for positions
    //float objective_function(const std::vector<float> &position);

    // Set the first global best for a vector of particles
    void initialize_global_best();

    // Goes through all the particles and sets the global best to the particle with the smallest fitness
    void update_global_best();

    // Initialize and return n particles with random values
    void initialize_positions();
    void initialize_positions(std::vector<Particle> &particles);

    // Update the position of all particles with positions
    void update_positions(std::vector<Particle> &particles, const std::vector<std::vector<double>> &new_positions);

    // Update the position of all particles with positions and fitness
    void update_particles(std::vector<Particle> &particles, const std::vector<std::vector<double>> &pos, const std::vector<double> &fit);

    // Goes through all the particles, calculates the fitness and assigns to the particle
    void calculate_set_fitness();
    void calculate_set_fitness(std::vector<Particle> &particles);

    void sort_particles();

    void initialize_optimization();
    void initialize_optimization(std::vector<Particle> &particles);

    bool stopping_condition(const double gb_fitness, int &stopping_counter, float &stop_condition, const int i);

protected:
    int n_particles;                    // number of particles
    int rank;                           // rank of the polynomial polynomial_function
    int max_iter;                       // max number of algorithm iterations
    float threshold;                    // stop if global best bellow threshold
    std::vector<float> min_pos;
    std::vector<float> max_pos;
    Particle global_best;               // global best
    std::vector<Particle> particles;
};


#endif //DISSERTATION_NILM_OPTIMIZATION_H
