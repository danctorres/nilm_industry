//
// Created by danctorres on 4/3/2023.
//

#include "AC.h"


void AC::set_number_ants(const int number_ants) {
    this->number_ants = number_ants;
}

void AC::set_q(const float q) {
    this->q = q;
}

void AC::set_xi(const float xi) {
    this->xi = xi;
}

void AC::set_x_min(const int x_min) {
    this->x_min = x_min;
}

void AC::set_x_max(const int x_max) {
    this->x_max = x_max;
}

void AC::set_weights(const std::vector<float> &weights) {
    this->weights = weights;
}

void AC::set_probabilities(const std::vector<float> &probabilities) {
    this->probabilities = probabilities;
}

int AC::get_number_ants() const {
    return number_ants;
}

float AC::get_q() const {
    return q;
}

float AC::get_xi() const {
    return xi;
}

float AC::get_x_min() const {
    return x_min;
}

float AC::get_x_max() const {
    return x_max;
}

std::vector<float> AC::get_weights() const {
    return weights;
}

std::vector<float> AC::get_probabilities() const {
    return probabilities;
}

void AC::initialize_weights() {
    float weight = 0.0f;
    weights.clear();
    for (int i = 1; i <= n_particles; i++){
        weight = (1 / (q * n_particles * sqrt(2 * std::numbers::pi)) ) * exp(- pow(i - 1, 2) / ((2 * pow(q, 2) * pow(n_particles, 2))));
        this->weights.push_back(weight);
    }
}

std::vector<float> AC::calculate_probabilities() {
    std::vector<float> probs;
    float sum_weights = std::accumulate(weights.begin(), weights.end(), 0.0f);
    // The number of solutions is equal to the number of particles
    for (int i = 0; i < n_particles; i++){
        probs.push_back(weights[i] / sum_weights);
    }
    return probs;
}

// Each Gaussian kernel has one Gaussian function
// Returns vector of all the indexes for each ant
std::vector<int> AC::select_gaussian() {
    std::vector<int> gauss_idx;
    float rand_num;
    float cumulative_prob = 0.0f;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);
    // Selects one Gaussian function for each Gaussian Kernel
    for (int i = rank; i > 0 ; i--) {
        cumulative_prob = 0.0f;
        rand_num = dis(gen);
        for (int j = 0; j < probabilities.size(); j++) {
            cumulative_prob += probabilities[j];
            if (rand_num < cumulative_prob) {
                gauss_idx.push_back(j);
                break;
            }
        }
    }
    return gauss_idx;
}

// Create a vector with the std of all the Gaussian functions for one solution
std::vector<float> AC::calculate_all_std(const std::vector<int> &gaussian_index) {
    std::vector<float> std_vector;
    float stdeviation = 0.0f;

    // The rank is equal to number of Gaussian Kernels, and is equal to gaussian_index.size()
    for (int i = 0; i < rank; i++){
        stdeviation = 0.0f;
        // The n_particles is equal to the number of solutions
        for (int j = 0; j < n_particles; j++){
            stdeviation += fabs (particles[j].get_position()[i] - particles[gaussian_index[i]].get_position()[i]) / (n_particles - 1);
        }
        std_vector.push_back(stdeviation * xi);
    }
    return std_vector;
}

float AC::gaussian_function(const int dim, const int gaussian_index, const float sigma, const float x) {
    float coefficient = 1 / (sigma * sqrt(2 * std::numbers::pi));
    float exponential = - pow(x - particles[gaussian_index].get_position()[dim], 2) / (2 * pow(sigma, 2));
    return weights[gaussian_index] * coefficient * exp(exponential);
}

Particle AC::sample_new_particle(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector){
    std::vector<float> new_position;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(x_min, x_max);

    for (int i = 0; i < rank; i++){
        new_position.push_back(gaussian_function(i, gaussian_index[i], std_vector[i], dis(gen)));
    }
    return new_position;
}

AC::AC(const int n_particles, const int rank, const int max_iter, const float threshold,
                       const std::vector<float> &min_pos, const std::vector<float> &max_pos, const int number_ants,
                       const float q, const float xi, const int x_min, const int x_max)
                       : Optimization(n_particles, rank, max_iter, threshold, min_pos, max_pos) {
    this->number_ants = number_ants;
    this->q = q;
    this->xi = xi;
    this->x_min = x_min;
    this->x_max = x_max;

    initialize_optimization();
    sort_particles();                               // Sort particles in descending order
    initialize_weights();                           // Calculate the weight vector w
    set_probabilities(calculate_probabilities());   // Calculate the probability of selecting each Gaussian function

    std::cout << "- Number of solutions = " << n_particles << ", q = " << q << ", xi = " << xi << " -" << std::endl;
}

void AC::run(){
    std::vector<Particle> new_particles;
    std::vector<int> gaussian_index;
    std::vector<float> std_vector;

    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        for (int j = 0; j < number_ants; j++) {
            gaussian_index = select_gaussian();              // Select one Gaussian function per Gaussian kernel
            std_vector = calculate_all_std(gaussian_index);  // Vector with the std for each Gaussian function
            new_particles.push_back(Particle(sample_new_particle(gaussian_index, std_vector)));
        }
        calculate_set_fitness(new_particles);

        particles.insert(particles.end(), new_particles.begin(), new_particles.end());
        sort_particles();
        update_global_best();
        set_probabilities(calculate_probabilities());

        gaussian_index.clear();
        new_particles.clear();

        if (get_global_best().get_fitness() < 0.01){
            return;
        }
        else {
            if (stop_condition == get_global_best().get_fitness()) {
                if (stopping_counter >= 2 && get_global_best().get_fitness() < 0.1) {
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
