//
// Created by danie on 3/19/2023.
//

#ifndef DISSERTATION_NILM_PARTICLES_H
#define DISSERTATION_NILM_PARTICLES_H

#include <vector>
#include "Optimization.h"

class Particles : public Optimization{
public:
    Particles();

private:
    std::vector<std::vector<float>> position;
    std::vector<float> fitness;
};


#endif //DISSERTATION_NILM_PARTICLES_H
