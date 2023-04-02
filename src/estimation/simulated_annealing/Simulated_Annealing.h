//
// Created by danie on 3/16/2023.
//

#ifndef DISSERTATION_NILM_SIMULATED_ANNEALING_H
#define DISSERTATION_NILM_SIMULATED_ANNEALING_H

#include "../optimization_interface/Optimization.h"

class Simulated_Annealing : public Optimization {
    Simulated_Annealing(int n_particles, int rank, int max_iter);
    void set_temperature(float temperature);
    float get_temperature() const;

    void run();

private:
    float temperature;
};


#endif //DISSERTATION_NILM_SIMULATED_ANNEALING_H
