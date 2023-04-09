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


class Ant_Colony : public Optimization{
public:
    Ant_Colony(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float q, float xi, int x_min, int x_max);

    void set_q(const float q);
    void set_xi(const float xi);
    void set_x_min(const int x_min);
    void set_x_max(const int x_max);
    void set_weights(const std::vector<float> &weights);
    void set_probability_gaussians(const std::vector<float> &probability_gaussians);

    float get_q() const;
    float get_xi() const;
    float get_x_min() const;
    float get_x_max() const;
    std::vector<float> get_weights() const;
    std::vector<float> get_probability_gaussians() const;

    void initialize_weights();
    void initialize_probability_gaussians();
    void sort_particles();
    std::vector<int> select_gaussian();      // return Gaussian Index
    float calculate_std(const int gaussian_index);
    std::vector<float> calculate_all_std(const std::vector<int> &gaussian_index);
    float gaussian_function(const int ant_index, const int gaussian_index, const float sdt, const float x);
    std::vector<Particle> calculate_new_particles(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector);

    void run();

private:
    float q;
    float xi;
    int x_min;
    int x_max;
    std::vector<float> weights;
    std::vector<float> probability_gaussians;
};


#endif //DISSERTATION_NILM_ANT_COLONY_H
