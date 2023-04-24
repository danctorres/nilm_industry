//
// Created by danctorres on 4/3/2023.
//

#include "Newton.h"


std::vector<float> Newton::gradient(const std::vector<float> &position) {
    std::vector<float> grad = {2 * position[0], 2 * position[1]};
    return grad;
}

std::vector<float> Newton::hessian(const std::vector<float> &position) {
    std::vector<float> hess = {2.0f, 0.0f, 0.0f, 2.0f};
    return hess;
}

// The determinant is used to calculate the inverse of the Hessian
float Newton::determinant(const std::vector<float> &hess) {
    float det = hess[0]*hess[3] - hess[1]*hess[2];
    return det;
}

std::vector<float> Newton::step(const std::vector<float> &grad, const std::vector<float> &hess, float det, const Particle &particle) {
    float step_x = (hess[3] * grad[0] - hess[1] * grad[1]) / det;
    float step_y = (- hess[2] * grad[0] + hess[0] * grad[1]) / det;

    std::vector<float> new_position = {particle.get_position()[0] - step_x, particle.get_position()[1] - step_y};
    return new_position;
}


Newton::Newton(int n_particles, int rank, int max_iter, int min_pos, int max_pos) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    initialize_optimization();
}

void Newton::run() {
    std::vector<float> grad;
    std::vector<float> hess;
    float det;
    std::vector<float> new_position;

    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        for (Particle &particle: particles) {
            grad = gradient(particle.get_position());
            hess = hessian(particle.get_position());
            det = determinant(hess);

            if (det == 0){
                std::cout << "Determinant is zero" << std::endl;
                std::vector<float> position_solution = {0.0, 0.0};
                global_best.set_position(position_solution);
                global_best.set_fitness(0.0f);
                break;
            }

            new_position = step(grad, hess, det, particle);
            particle.set_position(new_position);
        }

        calculate_set_fitness();
        update_global_best();

        if (get_global_best().get_fitness() < 0.001){
            break;
        }
        else {
            if (stop_condition == get_global_best().get_fitness()) {
                if (stopping_counter >= 2 && get_global_best().get_fitness() < 0.01) {
                    std::cout << "- Number of cycles " << i << " - " << std::endl;
                    break;
                }
                stopping_counter++;
            } else {
                stopping_counter = 0;
                stop_condition = global_best.get_fitness();
            }
        }
    }
}
