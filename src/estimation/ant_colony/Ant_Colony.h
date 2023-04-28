//
// Created by danctorres on 4/3/2023.
//

#ifndef DISSERTATION_NILM_ANT_COLONY_H
#define DISSERTATION_NILM_ANT_COLONY_H

#include <algorithm>
#include <cmath>
#include <numeric>
#include <random>
#include <vector>
#include "../optimization_interface/Optimization.h"


// Ant colony optimization for continuous domains by Krzysztof Socha and Marco Dorigo
// One ant per solution

class Ant_Colony : public Optimization{
public:
    Ant_Colony(const int n_particles, const int rank, const int max_iter, const float threshold,
               const std::vector<float> &min_pos, const std::vector<float> &max_pos, const int number_ants,
               const float q, const float xi, const int x_min, const int x_max);

    void set_number_ants(const int number_ants);
    void set_q(const float q);
    void set_xi(const float xi);
    void set_x_min(const int x_min);
    void set_x_max(const int x_max);
    void set_weights(const std::vector<float> &weights);
    void set_probabilities(const std::vector<float> &prob_gauss_funcs);

    int get_number_ants() const;
    float get_q() const;
    float get_xi() const;
    float get_x_min() const;
    float get_x_max() const;
    std::vector<float> get_weights() const;
    std::vector<float> get_probabilities() const;

    void initialize_weights();
    std::vector<float> calculate_probabilities();
    std::vector<int> select_gaussian();      // return Gaussian Index
    std::vector<float> calculate_all_std(const std::vector<int> &gaussian_index);
    float gaussian_function(const int dimension, const int gaussian_index, const float std, const float x);
    Particle sample_new_particle(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector);


    void run();

private:
    int number_ants;
    float q;
    float xi;       // pheromone evaporation rate
    int x_min;
    int x_max;
    std::vector<float> weights;
    std::vector<float> probabilities;
};


#endif //DISSERTATION_NILM_ANT_COLONY_H
