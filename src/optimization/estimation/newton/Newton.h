//
// Created by danctorres on 4/3/2023.
//

#ifndef DISSERTATION_NILM_NEWTON_H
#define DISSERTATION_NILM_NEWTON_H

#include <vector>
#include "../optimization_interface/Optimization.h"


class Newton : public Optimization{
public:
    Newton(const int n_particles, const int rank, const int max_iter, const double threshold,
           std::vector<float> &min_pos, std::vector<float> &max_pos);

    std::vector<double> gradient(const std::vector<double> &position);
    std::vector<double> hessian(const std::vector<double> &position);

    double determinant(const std::vector<double> &hess);
    std::vector<double> step(const std::vector<double> &grad, const std::vector<double> &hess, const double det, const Particle &particle);

    void run();
};


#endif //DISSERTATION_NILM_NEWTON_H
