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
    std::vector<uint_fast32_t> get_parameter(const std::string name_parameter) const;
private:
    std::vector<uint_fast32_t> state_0;
    std::vector<uint_fast32_t> state_1;
    std::vector<uint_fast32_t> state_2;
    std::vector<uint_fast32_t> state_3;
    std::vector<uint_fast32_t> state_4;
    std::vector<uint_fast32_t> state_5;
};

#endif //DISSERTATION_NILM_STATE_READ_H
