//
// Created by danie on 3/7/2023.
//

#ifndef DISSERTATION_NILM_READ_STATE_H
#define DISSERTATION_NILM_READ_STATE_H

#include <string>
#include <vector>
#include "Read.h"

class Read_State : public Read{
public:

    Read_State(const std::string& name_file);

    std::vector<uint> get_parameter(const std::string& name_parameter) const;
    std::vector<std::vector<uint>> get_all_parameter() const;

private:
    std::vector<uint> state_0;
    std::vector<uint> state_1;
    std::vector<uint> state_2;
    std::vector<uint> state_3;
    std::vector<uint> state_4;
    std::vector<uint> state_5;
};

#endif //DISSERTATION_NILM_READ_STATE_H
