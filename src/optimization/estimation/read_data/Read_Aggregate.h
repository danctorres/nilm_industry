//
// Created by danctorres on 3/5/23.
//

#ifndef DISSERTATION_NILM_READ_AGGREGATE_H
#define DISSERTATION_NILM_READ_AGGREGATE_H

#include <iostream>
#include <string>
#include <vector>
#include "Read.h"


class Read_Aggregate : public Read {
public:
    Read_Aggregate(const std::string& name_file);

    float get_one_parameter(const std::string &name_parameter, const int sample) const;
    std::vector<float> get_parameters(const std::string &name_parameter) const;
    std::vector<std::vector<float>> get_all_parameters() const;
    int size();
private:
    std::vector<float> timestamp;
    std::vector<float> active_power;
    std::vector<float> reactive_power;
    std::vector<float> apparent_power;
    std::vector<float> current;
    std::vector<float> voltage;
    std::vector<float> power_factor;
};


#endif //DISSERTATION_NILM_READ_AGGREGATE_H
