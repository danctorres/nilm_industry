//
// Created by danie on 3/7/2023.
//

#ifndef DISSERTATION_NILM_STATE_READ_H
#define DISSERTATION_NILM_STATE_READ_H

#include "Read.h"
#include <string>
#include <vector>

class State_Read : public Read{
public:
    // setters
    void set_parameters();

    // getters
    std::vector<int> get_parameter(const std::string name_parameter) const;
private:
    std::vector<int> state_0;
    std::vector<int> state_1;
    std::vector<int> state_2;
    std::vector<int> state_3;
    std::vector<int> state_4;
    std::vector<int> state_5;
};

#endif //DISSERTATION_NILM_STATE_READ_H
