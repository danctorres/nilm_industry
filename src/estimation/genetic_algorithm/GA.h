//
// Created by danie on 4/25/2023.
//

#ifndef DISSERTATION_NILM_GA_H
#define DISSERTATION_NILM_GA_H

#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include "../optimization_interface/Optimization.h"


// A new genetic algorithm for global optimization of multimodal continuous functions by Manoj Thakur
// Selection: Tournament
// Crossover: Double Pareto crossover (DPX)
// Mutation: Power mutation operator (PM)
// Elitism: Yes

class GA : public Optimization {
public:
    GA(int n_particles, int rank, int max_iter, std::vector<float> &min_pos, std::vector<float> &max_pos,
       const int n_tournaments, const float alpha, const float beta, const float p_dist, const int size_elite);

    void set_n_participants(const int n_participants);
    void set_n_tournaments(const int n_tournaments);
    void set_alpha(const float alpha);
    void set_beta(const float beta);
    void set_p_dist(const float p_dist);
    void set_size_elite(const float size_elite);

    int get_n_participants() const;
    int get_n_tournaments() const;
    float get_alpha() const;
    float get_beta() const;
    float get_p_dist() const;
    float get_size_elite() const;

    std::vector<int> selection();   // returns particle index, n_tournaments needs to be an even number, since the offsprings require a pair of parents
    std::vector<int> calculate_candidates_idx();
    std::vector<Particle> generate_offsprings(const Particle parent1, const Particle parent2);
    std::vector<Particle> crossover(const std::vector<int> &particles_idx);
    std::vector<float> mutation(std::vector<float> &particles_position);
    std::vector<Particle> elitism();
    void run();

private:
    int n_participants;
    int n_tournaments;
    float alpha;    // shape parameter
    float beta;     // scale parameter
    float p_dist;
    int size_elite;
};


#endif //DISSERTATION_NILM_GA_H
