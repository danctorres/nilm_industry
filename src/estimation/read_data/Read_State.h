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

    std::vector<int> get_parameter(const std::string& name_parameter) const;
    std::vector<std::vector<int>> get_all_parameter() const;

private:
    std::vector<int> state_0;
    std::vector<int> state_1;
    std::vector<int> state_2;
    std::vector<int> state_3;
    std::vector<int> state_4;
    std::vector<int> state_5;
};

#endif //DISSERTATION_NILM_READ_STATE_H
