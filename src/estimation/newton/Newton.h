//
// Created by danctorres on 4/3/2023.
//

#ifndef DISSERTATION_NILM_NEWTON_H
#define DISSERTATION_NILM_NEWTON_H

#include <vector>
#include "../optimization_interface/Optimization.h"


class Newton : public Optimization{
public:
    Newton(int n_particles, int rank, int max_iter, std::vector<float> &min_pos, std::vector<float> &max_pos);

    std::vector<float> gradient(const std::vector<float> &position);
    std::vector<float> hessian(const std::vector<float> &position);

    float determinant(const std::vector<float> &hess);
    std::vector<float> step(const std::vector<float> &grad, const std::vector<float> &hess, const Particle &particle);

    void run();
};


#endif //DISSERTATION_NILM_NEWTON_H
