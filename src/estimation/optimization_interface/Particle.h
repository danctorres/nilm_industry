//
// Created by dtorres on 3/19/2023.
//

#ifndef DISSERTATION_NILM_PARTICLE_H
#define DISSERTATION_NILM_PARTICLE_H

#include <vector>

class Particle{
public:
    Particle();
    Particle(std::vector<float> &position);
    Particle(std::vector<float> &position, float fitness);

    void set_position(const std::vector<float> &position);
    void set_fitness(const float fitness);
    void set_parameters(const std::vector<float> &position, const float fitness);
    void set_parameters_Particle(const Particle &particle);


    std::vector<float> get_position() const;
    float get_fitness() const;
protected:
    std::vector<float> position;
    float fitness;
};


#endif //DISSERTATION_NILM_PARTICLE_H
