//
// Created by danie on 4/28/2023.
//

#ifndef DISSERTATION_NILM_GD_H
#define DISSERTATION_NILM_GD_H

#include <vector>
#include "../optimization_interface/Optimization.h"

class GD : public Optimization{
public:
    GD(const int n_particles, const int rank, const int max_iter, const float threshold,
       const std::vector<float> &min_pos, const std::vector<float> &max_pos, const float step_size);

    void set_step_size(const float step_size);
    float get_step_size() const;

    std::vector<float> new_pos(const std::vector<float> &position);
    void run();

private:
    float step_size;
};


#endif //DISSERTATION_NILM_GD_H
