//
// Created by danctorres on 3/19/2023.
//

#ifndef DISSERTATION_NILM_PARTICLE_H
#define DISSERTATION_NILM_PARTICLE_H

#include <vector>


class Particle{
public:
    Particle();
    Particle(const std::vector<double> &position);
    Particle(const std::vector<double> &position, const double fitness);

    void set_position(const std::vector<double> &position);
    void set_fitness(const double fitness);
    void set_parameters(const std::vector<double> &position, const double fitness);
    void set_parameters_Particle(const Particle &particle);


    std::vector<double> get_position() const;
    double get_fitness() const;

protected:
    std::vector<double> position;
    double fitness;
};


#endif //DISSERTATION_NILM_PARTICLE_H
