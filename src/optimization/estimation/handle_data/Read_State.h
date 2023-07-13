//
// Created by danctorres on 3/7/2023.
//

#ifndef DISSERTATION_NILM_READ_STATE_H
#define DISSERTATION_NILM_READ_STATE_H

#include <iostream>
#include <string>
#include <vector>
#include "Read.h"


class Read_State : public Read {
public:
    Read_State(const std::string& name_file);

    std::vector<int> get_parameters(const int eq_idx) const;
    int get_one_parameter(const int eq_idx, const int sample) const;
    std::vector<std::vector<int>> get_all_parameter() const;

private:
    std::vector<std::vector<int>> states;
};

#endif //DISSERTATION_NILM_READ_STATE_H
