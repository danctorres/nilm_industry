//
// Created by danctorres on 08-05-2023.
//

#ifndef NILM_INDUSTRY_READ_EQ_H
#define NILM_INDUSTRY_READ_EQ_H

#include <string>
#include <vector>

#include "../../estimation/read_data/Read.h"

class Read_Eq : public Read {
public:
    Read_Eq(const std::string& name_file);

    std::vector<float> get_eq(const int eq_idx) const;
private:
    std::vector<float> actual_eq0;
    std::vector<float> actual_eq1;
    std::vector<float> actual_eq2;
    std::vector<float> actual_eq3;
    std::vector<float> actual_eq4;
    std::vector<float> actual_eq5;
};


#endif //NILM_INDUSTRY_READ_EQ_H
