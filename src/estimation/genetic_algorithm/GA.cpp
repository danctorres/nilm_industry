//
// Created by danie on 4/25/2023.
//

#include "GA.h"


void GA::set_n_participants(const int n_participants) {
    this->n_participants = n_participants;
}

void GA::set_n_tournaments(const int n_tournaments) {
    this->n_tournaments = n_tournaments;
}

void GA::set_alpha(const float alpha) {
    this->alpha = alpha;
}

void GA::set_beta(const float beta) {
    this->beta = beta;
}

void GA::set_p_dist(const float p_dist) {
    this->p_dist = p_dist;
}

void GA::set_size_elite(const float size_elite) {
    this->size_elite = size_elite;
}

int GA::get_n_participants() const {
    return n_participants;
}

int GA::get_n_tournaments() const {
    return n_tournaments;
}

float GA::get_alpha() const {
    return alpha;
}

float GA::get_beta() const {
    return beta;
}

float GA::get_p_dist() const {
    return p_dist;
}

float GA::get_size_elite() const {
    return size_elite;
}


std::vector<int> GA::calculate_candidates_idx() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0, n_particles - 1);

    std::vector<int> selected_idx;
    int idx = dis(gen);
    selected_idx.push_back(idx);
    int i = 0;
    // Vector should only be composed of unique values
    while (i < n_participants - 1) {
        idx = dis(gen);
        if (std::count(selected_idx.begin(), selected_idx.end(), idx)) {}
        else {
            selected_idx.push_back(idx);
            i++;
        }
    }
    return selected_idx;
}

std::vector<int> GA::selection() {
    std::vector<int> idx;
    std::vector<int> selected_idx;

    int max_index = 0;
    for (int i = 0; i < n_tournaments; i++) {
        idx = calculate_candidates_idx();
        max_index = particles[0].get_fitness();

        // Get the particle with the max fitness from the candidates
        for (int i = 1; i < idx.size(); i++) {
            if (max_index < particles[idx[i]].get_fitness()) {
                max_index = idx[i];
            }
        }
        selected_idx.push_back(max_index);
        idx.clear();
    }
    return selected_idx;
}

// Equations accordingly to "A new mutation operator for real coded genetic algorithms" by Kusum Deep Manoj Thakur
std::vector<float> GA::mutation(std::vector<float> &particles_position) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);

    //float s = p_dist * pow(dis(gen), p_dist - 1);
    float s = pow(dis(gen), 1 / p_dist);

    for (int i = 0; i < particles_position.size(); i++) {
        if ( ((particles_position[i] - min_pos[i]) / (max_pos[i] - particles_position[i])) < dis(gen)) {
                particles_position[i] -= s * (particles_position[i] - min_pos[i]);
        }
        else {
            particles_position[i] += s * (max_pos[i] - particles_position[i]);
        }
    }
    return particles_position;
}

std::vector<Particle> GA::generate_offsprings(const Particle parent1, const Particle parent2) {
    std::vector<Particle> offsprings;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0f, 1.0f);
    float rand_num = dis(gen);

    float Bi = 0.0f;
    if (rand_num < 0.5f) {
        Bi = alpha * beta * (1 - pow(2 * rand_num, -1 / alpha));
    }
    else {
        Bi = alpha * beta * (pow(1 - 2 * rand_num, -1 / alpha) - 1);
    }

    std::vector<float> pos_off1;
    std::vector<float> pos_off2;

    for (int i = 0; i < rank; i++) {
        pos_off1.push_back( (parent1.get_position()[i] + parent2.get_position()[i] + Bi * fabs(parent1.get_position()[i] - parent2.get_position()[i])) / 2);
        pos_off2.push_back( (parent1.get_position()[i] + parent2.get_position()[i] - Bi * fabs(parent1.get_position()[i] - parent2.get_position()[i])) / 2);
    }

    offsprings.push_back(Particle(mutation(pos_off1)));
    offsprings.push_back(Particle(mutation(pos_off2)));

    return offsprings;
}

std::vector<Particle> GA::crossover(const std::vector<int> &particles_idx) {
    std::vector<Particle> offsprings;
    std::vector<Particle> new_particles;

    // Go 2 by 2
    for (int i = 0; i < particles_idx.size(); i += 2) {
        new_particles = generate_offsprings(particles[i], particles[i + 1]);
        offsprings.insert(offsprings.end(), new_particles.begin(), new_particles.end());
    }
    return offsprings;
}

std::vector<Particle> GA::elitism() {
    std::vector<Particle> elite;
    sort_particles();
    for (int i = 0; i < size_elite; i++) {
        elite.push_back(particles[i]);
    }
    return elite;
}

GA::GA(int n_particles, int rank, int max_iter, std::vector<float> &min_pos, std::vector<float> &max_pos,
       const int n_tournaments, const float alpha, const float beta, const float p_dist,
       const int size_elite) : Optimization(n_particles, rank, max_iter, min_pos, max_pos) {

    if (n_tournaments % 2 != 0) {
        throw std::runtime_error("Error: n_tournaments is not even.");
    }

    this->n_participants = n_particles / n_tournaments;
    this->n_tournaments = n_tournaments;
    this->alpha = alpha;
    this->beta = beta;
    this->p_dist = p_dist;
    this->size_elite = size_elite;

    initialize_optimization();
    std::cout << "- Number of particles = " << n_particles << ", ";
    std::cout << "number of participants = " << n_participants << ", ";
    std::cout << "number of tournaments = " << n_tournaments << ", ";
    std::cout << "shape parameter = " << alpha << ", ";
    std::cout << "scale parameter = " << beta << ", ";
    std::cout << "mutation parameter = " << p_dist << ", ";
    std::cout << "elite size = " << size_elite << " -" << std::endl;
}

void GA::run() {
    float stop_condition = global_best.get_fitness();
    int stopping_counter = 0;

    std::vector<Particle> new_particles;
    std::vector<Particle> cross_particles;

    for (int i = 0; i < max_iter; i++) {
        new_particles = elitism();
        cross_particles = crossover(selection());
        new_particles.insert(new_particles.end(), cross_particles.begin(), cross_particles.end());
        particles.clear();
        set_particles(new_particles);
        calculate_set_fitness();
        initialize_global_best();
        new_particles.clear();
        // Stopping conditions
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
