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
    std::vector<uint_fast32_t> get_parameter(const std::string name_parameter) const;

private:
    std::vector<uint_fast32_t> timestamp;
    std::vector<uint_fast32_t> active_power;
    std::vector<uint_fast32_t> reactive_power;
    std::vector<uint_fast32_t> apparent_power;
    std::vector<uint_fast32_t> current;
    std::vector<uint_fast32_t> voltage;
    std::vector<uint_fast32_t> power_factor;
};


#endif //DISSERTATION_NILM_AGGREGATE_READ_H
