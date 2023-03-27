//
// Created by dtorres on 3/16/2023.
//

#ifndef DISSERTATION_NILM_OPTIMIZATION_H
#define DISSERTATION_NILM_OPTIMIZATION_H
#include <vector>

class Optimization {
public:
    Optimization();
    Optimization(int n_particles, int rank, int max_iter);
    void set_n_particles(uint n_particles);
    void set_rank(uint rank);
    void set_max_iter(uint max_iter);
    uint get_n_particles();
    uint get_rank();
    uint get_max_iter();
    float objective_function(std::vector<float> position);

private:
    uint n_particles;    // number of particles
    uint rank;           // rank of the polynomial function
    uint max_iter;       // max number of algorithm iterations
};


#endif //DISSERTATION_NILM_OPTIMIZATION_H
