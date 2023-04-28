//
// Created by danie on 4/28/2023.
//

#include "GD.h"

void GD::set_step_size(const float step_size) {
    this->step_size = step_size;
}

float GD::get_step_size() const {
    return step_size;
}

// Hard-coded gradient
std::vector<float> GD::new_pos(const std::vector<float> &position) {
    std::vector<float> new_pos;
    std::vector<float> grad = {2 * (position[0] + 3), 1.0f};
    for (int i = 0; i < rank ; i++){
        new_pos.push_back(position[i] - step_size * grad[i]);
    }
    return new_pos;
}

GD::GD(const int n_particles, const int rank, const int max_iter, const float threshold,
       const std::vector<float> &min_pos, const std::vector<float> &max_pos, const float step_size)
       : Optimization(n_particles, rank, max_iter, threshold, min_pos, max_pos) {
    this->step_size = step_size;
    this->threshold = threshold;

    initialize_optimization();
}

void GD::run() {
    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        for (Particle &par : particles) {
            par.set_position(new_pos(par.get_position()));
        }
        calculate_set_fitness();
        update_global_best();

        if (stopping_condition(global_best.get_fitness(), stopping_counter, stop_condition, i)) {
            return;
        }
    }
    std::cout << "- Number of cycles " << max_iter << " - " << std::endl;
}
