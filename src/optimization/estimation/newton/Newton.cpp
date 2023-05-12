//
// Created by danctorres on 4/3/2023.
//

#include "Newton.h"


// The Newton functions are hard-coded
std::vector<double> Newton::gradient(const std::vector<double> &position) {
    std::vector<double> grad = {2 * (position[0] + 3), 1.0};
    return grad;
}

std::vector<double> Newton::hessian(const std::vector<double> &position) {
    std::vector<double> hess = {2.0, 0.0, 0.0, 0.0};
    return hess;
}

// The determinant is used to calculate the inverse of the Hessian
double Newton::determinant(const std::vector<double> &hess) {
    double det = hess[0] * hess[3] - hess[1] * hess[2];
    return det;
}

std::vector<double> Newton::step(const std::vector<double> &grad, const std::vector<double> &hess, const double det, const Particle &particle) {
    // step = inverse of the Hessian * gradient
    double step_x = (hess[3] * grad[0] - hess[1] * grad[1]) * ( 1 / det);
    double step_y = (- hess[2] * grad[0] + hess[0] * grad[1]) * ( 1 / det);

    // double step_x = -1.0 / hess[0] * grad[0] - 1.0 / hess[1] * grad[1];
    // double step_y = -1.0 / hess[2] * grad[0] -  1.0 / hess[3] * grad[1];

    std::vector<double> new_position = {particle.get_position()[0] - step_x, particle.get_position()[1] - step_y};
    return new_position;
}

Newton::Newton(const int n_particles, const int rank, const int max_iter, const double threshold,
               std::vector<float> &min_pos, std::vector<float> &max_pos) : Optimization(n_particles, rank, max_iter,
                                                                                        threshold, min_pos, max_pos) {
    initialize_optimization();
    std::cout << "- Number of particles = " << n_particles << std::endl;
}

void Newton::run() {
    std::vector<double> grad;
    std::vector<double> hess;
    double det;
    std::vector<double> new_position;

    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        for (Particle &par: particles) {
            hess = hessian(par.get_position());

            if (std::count(hess.begin(), hess.end(), 0)){
                std::cout << "The Hessian is non invertible."
                             " Newton method is not applicable to the objective polynomial_function." << std::endl;
                calculate_set_fitness();
                update_global_best();
                return;
            }

            par.set_position(step(gradient(par.get_position()), hess, determinant(hess), par));
        }

        calculate_set_fitness();
        update_global_best();

        std::cout << "Fit: " << get_global_best().get_fitness() << std::endl;

        if (stopping_condition(global_best.get_fitness(), stopping_counter, stop_condition, i)) {
            return;
        }
    }
    std::cout << "- Number of cycles " << max_iter << " - " << std::endl;
}
