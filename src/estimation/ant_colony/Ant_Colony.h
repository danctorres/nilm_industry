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
    Ant_Colony(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float q, float xi);

    void set_q(const float q);
    void set_xi(const float xi);
    void set_weights(const std::vector<float> &weights);
    void set_gaussians(const std::vector<float> &gaussians);
    void set_probability_gaussians(const std::vector<float> &probability_gaussians);


    float get_q() const;
    float get_xi() const;
    std::vector<float> get_weights() const;
    std::vector<float> get_gaussians() const;
    std::vector<float> get_probability_gaussians() const;

    void initialize_weights();
    void initialize_probability_gaussians();
    void sort_particles();
    int select_gaussian();      // return Gaussian Index

private:
    float q;
    float xi;
    std::vector<float> weights;
    std::vector<float> gaussians;
    std::vector<float> probability_gaussians;
};


#endif //DISSERTATION_NILM_ANT_COLONY_H
