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

void Ant_Colony::set_gaussians(const std::vector<float> &gaussians) {
    this->gaussians = std::move(gaussians);
}

void Ant_Colony::set_weights(const std::vector<float> &weights) {
    this->gaussians = std::move(weights);
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

std::vector<float> Ant_Colony::get_gaussians() const {
    return gaussians;
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
        weight = 1 / (q * n_particles * sqrt(2 * std::numbers::pi) * exp(- (pow((i - 1), 2) / (pow(2 * pow(q, 2) * pow(n_particles, 2))))));
        this->weights.push_back(weight);
    }
}

void Ant_Colony::sort_particles() {
    std::sort(particles.begin(), particles.end(), [](const Particle& par1, const Particle& par2) {
        return par1.get_fitness() < par2.get_fitness();
    });
}

void Ant_Colony::initialize_probability_gaussians() {
    float probability = 0.0f;
    float sum_weights = std::accumulate(weights.begin(), weights.end(), 0);
    for (int i = 0; i < rank; i++){
        probability_gaussians.push_back(weights[i] / sum_weights);
    }
}

int Ant_Colony::select_gaussian() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);
    for (int i = 0; i < probability_gaussians.size(); i++){
        if(dis(gen) > probability_gaussians){
            return i;
            break;
        }
    }
}

Ant_Colony::Ant_Colony(int n_particles, int rank, int max_iter, int min_pos, int max_pos, float q, float xi) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {
    this->q = q;
    this->xi = xi;

    initialize_weights();
    initialize_probability_gaussians();
    initialize_optimization();

    sort_particles();
    select_gaussian();

}