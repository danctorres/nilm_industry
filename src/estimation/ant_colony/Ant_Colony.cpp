//
// Created by danctorres on 4/3/2023.
//

#include "Ant_Colony.h"


void Ant_Colony::set_q(const float q) {
    this->q = q;
}

void Ant_Colony::set_xi(const float xi) {
    this->xi = xi;
}

void Ant_Colony::set_x_min(const int x_min) {
    this->x_min = x_min;
}

void Ant_Colony::set_x_max(const int x_max) {
    this->x_max = x_max;
}

void Ant_Colony::set_weights(const std::vector<float> &weights) {
    this->weights = std::move(weights);
}

void Ant_Colony::set_prob_gauss_funcs(const std::vector<float> &prob_gauss_funcs) {
    this->prob_gauss_funcs = std::move(prob_gauss_funcs);
}

float Ant_Colony::get_q() const {
    return q;
}

float Ant_Colony::get_xi() const {
    return xi;
}

float Ant_Colony::get_x_min() const {
    return x_min;
}

float Ant_Colony::get_x_max() const {
    return x_max;
}

std::vector<float> Ant_Colony::get_weights() const {
    return weights;
}

std::vector<float> Ant_Colony::get_prob_gauss_funcs() const {
    return prob_gauss_funcs;
}

void Ant_Colony::initialize_weights() {
    float weight = 0.0f;
    weights.clear();
    for (int i = 1; i <= n_particles; i++){
        weight = (1 / (q * n_particles * sqrt(2 * std::numbers::pi)) ) * exp(- pow(i - 1, 2) / (2 * pow(q, 2) * pow(n_particles, 2)));
        std::cout << "Weights: " << weight << std::endl;
        this->weights.push_back(weight);
    }
}

void Ant_Colony::sort_particles() {
    std::sort(particles.begin(), particles.end(), [](const Particle& par1, const Particle& par2) {
        return par1.get_fitness() < par2.get_fitness();
    });
    std::cout << "Sorted First: " << particles[0].get_fitness() << " Last: " << particles[particles.size()].get_fitness() << std::endl;
}

void Ant_Colony::initialize_prob_gauss_funcs() {
    float sum_weights = std::accumulate(weights.begin(), weights.end(), 0.0f);
    // The number of solutions is equal to the number of particles
    for (int i = 0; i < n_particles; i++){
        prob_gauss_funcs.push_back(weights[i] / sum_weights);
        std::cout << "Initialize probability Gaussian functions: " << prob_gauss_funcs[i] << std::endl;
    }
}

// Each Gaussian kernel has one Gaussian function
// Returns vector of all the indexes for each ant
std::vector<int> Ant_Colony::select_gaussian() {
    std::vector<int> gauss_funcs_idx;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);
    // Selects one Gaussian function for each Gaussian Kernel
    for (int i = rank; i > 0 ; i--) {
        // Goes through the probabilities in ascending order
        for (int j = 0; j < prob_gauss_funcs.size(); j++) {
            float random_number = dis(gen);
            if (random_number < prob_gauss_funcs[j]) {
                gauss_funcs_idx.push_back(j);
                std::cout << "Random number: " << random_number << " -> Gaussian function index selected: " << j << std::endl;
                break;
            }
        }
    }
    return gauss_funcs_idx;
}


// Create a vector with the std of all the Gaussian functions for one solution
std::vector<float> Ant_Colony::calculate_all_std(const std::vector<int> &gaussian_index, const int solution_index) {
    std::vector<float> std_vector;
    float std = 0.0f;

    // The rank is equal to number of Gaussian Kernels, and is equal to gaussian_index.size()
    for (int i = 0; i < rank; i++){
        // The n_particles is equal to the number of solutions
        for (int j = 0; j < n_particles; j++){
            //std::cout << "Debugging Std 1: " << particles[solution_index].get_position()[j] - particles[solution_index].get_position()[gaussian_index[i]] << std::endl;
            //std::cout << "Debugging Std 2: " << sqrt(pow(particles[solution_index].get_position()[j] - particles[solution_index].get_position()[gaussian_index[i]], 2)) << std::endl;
            std += sqrt(pow(particles[solution_index].get_position()[j] - particles[solution_index].get_position()[gaussian_index[i]], 2)) / (n_particles - 1);
            //std::cout << "Debugging Std: " << std << std::endl;

        }
        std::cout << "Std: " << std << " solution index " << solution_index << std::endl;
        std_vector.push_back(std * xi);
        std = 0.0f;
    }
    return std_vector;
}

float Ant_Colony::gaussian_function(const int ant_index, const int gaussian_index, const float std, const float x) {
    std::vector<float> median_positions = particles[ant_index].get_position();
    std::cout << "Gaussian function: " << ( 1 / (std * sqrt(2 * std::numbers::pi)) * exp(-( pow((x - median_positions[gaussian_index]), 2) / (2 * pow(std, 2)) ))) << std::endl;
    return weights[ant_index] * ( 1 / (std * sqrt(2 * std::numbers::pi)) * exp(-( pow((x - median_positions[gaussian_index]), 2) / (2 * pow(std, 2)) )));
}

Particle Ant_Colony::calculate_new_particle(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector){
    std::vector<float> new_position;
    // Calculate the new position
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(x_min, x_max);
    for (int i = 0; i < rank; i++){
        new_position.push_back(gaussian_function(i, gaussian_index[i], std_vector[i], dis(gen)));
        std::cout << "New position: " << new_position[i] << std::endl;
    }
    return new_position;
}


Ant_Colony::Ant_Colony(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float q, float xi, int x_min, int x_max) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    this->q = q;
    this->xi = xi;
    this->x_min = x_min;
    this->x_max = x_max;

    initialize_weights();                   // Calculate the weight vector w
    initialize_prob_gauss_funcs();     // Calculate the probability of selecting each Gaussian function
    initialize_optimization();

    sort_particles();                       // sort particles in descending order
}

void Ant_Colony::run(){
    std::vector<Particle> new_particles;
    std::vector<int> gaussian_index;
    std::vector<float> std_vector;

    int stopping_counter = 0;
    float stop_condition = global_best.get_fitness();

    for (int i = 0; i < max_iter; i++) {
        std::cout << "---------------------- New iter number: " << i << "---------------------- " << std::endl;
        for (int j = 0; j < n_particles; j++) {
            gaussian_index = std::move(select_gaussian());  // Select one Gaussian function
            //std::cout << "Particle number: " << j <<std::endl;
            std_vector = std::move(calculate_all_std(gaussian_index, j));
            //}
            new_particles.push_back(Particle(calculate_new_particle(gaussian_index, std_vector)));
        }
        calculate_set_fitness(new_particles);
        std::cout << "New particle fit: " << new_particles[0].get_fitness() << std::endl;

        particles.insert(particles.end(), new_particles.begin(), new_particles.end());
        sort_particles();
        particles.erase(particles.end() - n_particles, particles.end());
        new_particles.clear();

        update_global_best();

        std::cout << "Global best fitness: " << global_best.get_fitness() << std::endl;
        std::cout << "Global best pos x: " << global_best.get_position()[0] << ", pos y: " << global_best.get_position()[1] << std::endl;

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
