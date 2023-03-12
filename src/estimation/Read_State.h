//
// Created by danie on 3/7/2023.
//

#ifndef DISSERTATION_NILM_READ_STATE_H
#define DISSERTATION_NILM_READ_STATE_H

#include "Read.h"
#include <string>
#include <vector>

class Read_State : public Read{
public:
    // setters
    void set_parameters();

    // getters
    std::vector<uint32_t> get_parameter(std::string name_parameter) const;
    std::vector<std::vector<uint32_t>> get_all_parameter() const;

private:
    std::vector<uint32_t> state_0;
    std::vector<uint32_t> state_1;
    std::vector<uint32_t> state_2;
    std::vector<uint32_t> state_3;
    std::vector<uint32_t> state_4;
    std::vector<uint32_t> state_5;
};

#endif //DISSERTATION_NILM_READ_STATE_H
