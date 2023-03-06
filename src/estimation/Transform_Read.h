//
// Created by dtorres on 3/5/23.
//

#ifndef DISSERTATION_NILM_TRANSFORM_READ_H
#define DISSERTATION_NILM_TRANSFORM_READ_H

#include "Read.h"
#include <string>
#include <vector>

class Transform_Read : public Read{
public:
    // setters
    void set_parameters();

    // getters
    std::vector<std::string> get_parameter(const std::string name_parameter) const;

    void print_parameter(const std::vector<std::string> &parameter) const;

private:
    std::vector<std::string> timestamp;
    std::vector<std::string> active_power;
    std::vector<std::string> reactive_power;
    std::vector<std::string> apparent_power;
    std::vector<std::string> current;
    std::vector<std::string> voltage;
    std::vector<std::string> power_factor;
};


#endif //DISSERTATION_NILM_TRANSFORM_READ_H
