//
// Created by danctorres on 3/16/2023.
//

#ifndef DISSERTATION_NILM_SIMULATED_ANNEALING_H
#define DISSERTATION_NILM_SIMULATED_ANNEALING_H

#include <cmath>
#include "../optimization_interface/Optimization.h"


class Simulated_Annealing : public Optimization {
public:
    Simulated_Annealing(const int n_particles, const int rank, const int max_iter, const float threshold,
                        const std::vector<float> &min_pos, const std::vector<float> &max_pos,
                        const float temperature, const float temp_min, const float cooling_factor);
    void set_temperature(float temperature);
    void set_temp_min(float temp_min);
    void set_cooling_factor(float cooling_factor);
    void set_last_fitness();
    float get_temperature() const;
    float get_temp_min() const;
    float get_cooling_factor() const;
    std::vector<float> get_last_fitness() const;

    float calculate_new_fitness(const std::vector<float> &new_positions);

    void run();

private:
    float temperature;
    float temp_min;
    float cooling_factor;
    std::vector<float> last_fitness;
};


#endif //DISSERTATION_NILM_SIMULATED_ANNEALING_H
