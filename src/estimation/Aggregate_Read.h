//
// Created by dtorres on 3/5/23.
//

#ifndef DISSERTATION_NILM_AGGREGATE_READ_H
#define DISSERTATION_NILM_AGGREGATE_READ_H

#include "Read.h"
#include <string>
#include <vector>

class Aggregate_Read : public Read{
public:
    // setters
    void set_parameters();
    // getters
    std::vector<int> get_parameter(const std::string name_parameter) const;

private:
    std::vector<int> timestamp;
    std::vector<int> active_power;
    std::vector<int> reactive_power;
    std::vector<int> apparent_power;
    std::vector<int> current;
    std::vector<int> voltage;
    std::vector<int> power_factor;
};


#endif //DISSERTATION_NILM_AGGREGATE_READ_H
