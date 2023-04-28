//
// Created by danctorres on 4/3/2023.
//

#include "Newton.h"


// The Newton functions are hard-coded
std::vector<float> Newton::gradient(const std::vector<float> &position) {
    std::vector<float> grad = {2 * (position[0] + 3), 1.0f};
    return grad;
}

std::vector<float> Newton::hessian(const std::vector<float> &position) {
    std::vector<float> hess = {2.0f, 0.0f, 0.0f, 0.0f};
    return hess;
}

// The determinant is used to calculate the inverse of the Hessian
/*float Newton::determinant(const std::vector<float> &hess) {
    float det = hess[0] * hess[3] - hess[1] * hess[2];
    return det;
}*/

std::vector<float> Newton::step(const std::vector<float> &grad, const std::vector<float> &hess, const Particle &particle) {
    //float step_x = (hess[3] * grad[0] - hess[1] * grad[1]) / det;
    //float step_y = (- hess[2] * grad[0] + hess[0] * grad[1]) / det;
    float step_x = -1.0 / hess[0] * grad[0] - 1.0 / hess[1] * grad[1];
    float step_y = -1.0 / hess[2] * grad[0] -  1.0 / hess[3] * grad[1];

    std::vector<float> new_position = {particle.get_position()[0] - step_x, particle.get_position()[1] - step_y};
    return new_position;
}

Newton::Newton(int n_particles, int rank, int max_iter, std::vector<float> &min_pos, std::vector<float> &max_pos) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    initialize_optimization();
    std::cout << "- Number of particles = " << n_particles << std::endl;
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
            //det = determinant(hess);

            if (std::count(hess.begin(), hess.end(), 0)){
                std::cout << "The Hessian is non invertible."
                             " Newton method is not applicable to the objective function." << std::endl;
                calculate_set_fitness();
                update_global_best();
                return;
            }

            new_position = step(grad, hess, particle);
            particle.set_position(new_position);
        }

        calculate_set_fitness();
        update_global_best();

        std::cout << "Fit: " << get_global_best().get_fitness() << std::endl;

        if (get_global_best().get_fitness() < 0.001){
            return;
        }
        else {
            if (stop_condition == get_global_best().get_fitness()) {
                if (stopping_counter >= 2 && get_global_best().get_fitness() < 0.01) {
                    std::cout << "- Number of cycles " << i << " - " << std::endl;
                    return;
                }
                stopping_counter++;
            } else {
                stopping_counter = 0;
                stop_condition = global_best.get_fitness();
            }
        }
    }
    std::cout << "- Number of cycles " << max_iter << " - " << std::endl;
}
