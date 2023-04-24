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
    void set_prob_gauss_funcs(const std::vector<float> &prob_gauss_funcs);

    float get_q() const;
    float get_xi() const;
    float get_x_min() const;
    float get_x_max() const;
    std::vector<float> get_weights() const;
    std::vector<float> get_prob_gauss_funcs() const;

    void initialize_weights();
    void initialize_prob_gauss_funcs();
    void sort_particles();
    std::vector<int> select_gaussian();      // return Gaussian Index
    std::vector<float> calculate_all_std(const std::vector<int> &gaussian_index, const int solution_index);
    float gaussian_function(const int ant_index, const int gaussian_index, const float std, const float x);
    Particle calculate_new_particle(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector);

    void run();

private:
    float q;
    float xi;
    int x_min;
    int x_max;
    std::vector<float> weights;
    std::vector<float> prob_gauss_funcs;
};


#endif //DISSERTATION_NILM_ANT_COLONY_H
