//
// Created by dtorres on 3/16/2023.
//

#ifndef DISSERTATION_NILM_OPTIMIZATION_H
#define DISSERTATION_NILM_OPTIMIZATION_H
#include <vector>
#include <random>
#include "Particle.h"


class Optimization {
public:
    Optimization();
    Optimization(int n_particles, int rank, int max_iter);
    void set_n_particles(int n_particles);
    void set_rank(int rank);
    void set_max_iter(int max_iter);
    void set_global_best_parameters(const std::vector<float> &position, const float fitness);
    void set_global_best(const Particle &global_best);

    int get_n_particles() const;
    int get_rank() const;
    int get_max_iter() const;
    Particle get_global_best() const;

    // Returns fitness for positions
    float objective_function(std::vector<float> position);

    // Set the first global best for a vector of particles
    template<typename T>
    void initiate_global_best(std::vector<T> particles) {
        global_best = new T(particles.front());
        for (auto &part : particles) {
            if (part.get_fitness() > global_best.get_fitness()) {
                set_global_best(part);
            }
        }
    }

    // Goes through all the particles and sets the global best to the particle with the biggest fitness
    template<typename T>
    void update_global_best(const std::vector<T> &particles) {
        for (auto &part : particles) {
            if (part.get_fitness() > global_best.get_fitness()) {
                set_global_best(part);
            }
        }
    }

    // Initialize and return n particles with random values
    template<typename T>
    void initialize_positions(std::vector<T> &particles, int min_pos, int max_pos) {
        for (int i = 0; i < n_particles; i++){
            std::vector<float> position;
            for (int j = 0; j < rank; j++) {
                std::random_device rd;
                std::mt19937 gen(rd());
                std::uniform_real_distribution<> dis(min_pos, max_pos);
                position.push_back(static_cast<float> (dis(gen)));
            }
            auto part = std::make_unique<T>(position);
            particles.push_back(*part);
        }
    }

    // Update the position of all particles with positions
    template<typename T>
    void update_positions(std::vector<T> &particles, const std::vector<std::vector<float>> &new_positions) {
        for (int i = 0; i < n_particles ; i++){
            particles[i].set_position(new_positions[i]);
        }
    }

    // Update the position of all particles with positions and fitness
    template<typename T>
    void update_particles(std::vector<T> &particles, const std::vector<std::vector<float>> &pos, const std::vector<float> &fit) {
        for (int i = 0; i < n_particles ; i++){
            particles[i].set_position(pos[i]);
            particles[i].set_fitness(fit[i]);
        }
    }

    // Goes through all the particles, calculates the fitness and assigns to the particle
    template<typename T>
    void calculate_set_fitness(std::vector<T> &particles) {
        std::for_each(particles.begin(), particles.end(), [this](Particle &par) {
            par.set_fitness(objective_function(par.get_position()));
        });
    }

private:
    int n_particles;                    // number of particles
    int rank;                           // rank of the polynomial function
    int max_iter;                       // max number of algorithm iterations
    Particle global_best;               // global best
};


#endif //DISSERTATION_NILM_OPTIMIZATION_H
