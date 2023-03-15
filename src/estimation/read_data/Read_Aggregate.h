//
// Created by dtorres on 3/5/23.
//

#ifndef DISSERTATION_NILM_READ_AGGREGATE_H
#define DISSERTATION_NILM_READ_AGGREGATE_H

#include "Read.h"
#include <string>
#include <vector>

class Read_Aggregate : public Read{
public:
    // setters
    void set_parameters();
    // getters
    [[nodiscard]] std::vector<uint32_t> get_parameter(std::string name_parameter) const;
    std::vector<std::vector<uint32_t>> get_all_parameters() const;

private:
    std::vector<uint32_t> timestamp;
    std::vector<uint32_t> active_power;
    std::vector<uint32_t> reactive_power;
    std::vector<uint32_t> apparent_power;
    std::vector<uint32_t> current;
    std::vector<uint32_t> voltage;
    std::vector<uint32_t> power_factor;
};


#endif //DISSERTATION_NILM_READ_AGGREGATE_H
