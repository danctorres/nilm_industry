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

void Ant_Colony::set_probability_gaussians(const std::vector<float> &probability_gaussians) {
    this->probability_gaussians = std::move(probability_gaussians);
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

std::vector<float> Ant_Colony::get_probability_gaussians() const {
    return probability_gaussians;
}

void Ant_Colony::initialize_weights() {
    float weight = 0.0f;
    weights.clear();
    for (int i = 0; i < n_particles; i++){
        weight = (1 / (q * n_particles * sqrt(2 * std::numbers::pi)) ) * exp(- pow(i - 1, 2) / (2 * pow(q, 2) * pow(n_particles, 2)));
        this->weights.push_back(weight);
    }
}

void Ant_Colony::sort_particles() {
    std::sort(particles.begin(), particles.end(), [](const Particle& par1, const Particle& par2) {
        return par1.get_fitness() < par2.get_fitness();
    });
}

void Ant_Colony::initialize_probability_gaussians() {
    float sum_weights = std::accumulate(weights.begin(), weights.end(), 0);
    for (int i = 0; i < rank; i++){
        probability_gaussians.push_back(weights[i] / sum_weights);
    }
}

// Each ant will has one Gaussian function
std::vector<int> Ant_Colony::select_gaussian() {
    std::vector<int> gaussian_index;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);
    for (int i = 0; i < n_particles; i++){
        for (int j = 0; j < probability_gaussians.size(); j++){
            if(dis(gen) > probability_gaussians[j]){
                gaussian_index.push_back(j);
                break;
            }
        }
    }
    return gaussian_index;
}

// Calculate the standard deviation for the selected Gaussian function
float Ant_Colony::calculate_std(const int gaussian_index) {
    float std = 0.0f;
    float median_position = particles[round(n_particles / 2)].get_position()[gaussian_index];
    for (int i = 0; i < n_particles; i++){
        std += (pow(sqrt(particles[i].get_position()[gaussian_index] - median_position), 2)) / (n_particles - 1);
    }
    return std;
}

// Create a vector with the std of all the Gaussian functions for each ant
std::vector<float> Ant_Colony::calculate_all_std(const std::vector<int> &gaussian_index) {
    std::vector<float> std_vector;
    for (const int &index : gaussian_index){
        std_vector.push_back(calculate_std(index));
    }
    return std_vector;
}

float Ant_Colony::gaussian_function(const int ant_index, const int gaussian_index, const float std, const float x) {
    std::vector<float> median_positions = particles[round(n_particles / 2)].get_position();
    return weights[ant_index] + ( 1 / (std * sqrt(2 * std::numbers::pi)) * exp(-( pow((x - median_positions[gaussian_index]), 2) / (2 * pow(std, 2)) )));
}

std::vector<Particle> Ant_Colony::calculate_new_particles(const std::vector<int> &gaussian_index, const std::vector<float> &std_vector){
    std::vector<Particle> new_particles;
    std::vector<float> positions;
    for (int i = 0; i < n_particles; i++){
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(x_min, x_max);

        positions = particles[i].get_position();
        positions[gaussian_index[i]] = gaussian_function(i, gaussian_index[i], std_vector[i], dis(gen));
        Particle new_particle = Particle(positions);
        new_particles.push_back(new_particle);
        positions.clear();
    }
    calculate_set_fitness(new_particles);
    return new_particles;
}


Ant_Colony::Ant_Colony(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float q, float xi, int x_min, int x_max) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    this->q = q;
    this->xi = xi;
    this->x_min = x_min;
    this->x_max = x_max;

    initialize_weights();
    initialize_probability_gaussians();
    initialize_optimization();

    sort_particles();
}

void Ant_Colony::run(){
    std::vector<int> gaussian_index;
    std::vector<float> std_vector;
    std::vector<Particle> new_particles;
    for (int i = 0; i < max_iter; i++) {
        gaussian_index = std::move(select_gaussian());
        std_vector = std::move(calculate_all_std(gaussian_index));
        new_particles = std::move(calculate_new_particles(gaussian_index, std_vector));
        particles.insert(particles.end(), new_particles.begin(), new_particles.end());
        sort_particles();
        particles.erase(particles.end() - n_particles, particles.end());

        gaussian_index.clear();
        std_vector.clear();
        new_particles.clear();
    }
}
