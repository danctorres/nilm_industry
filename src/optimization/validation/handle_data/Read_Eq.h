//
// Created by danctorres on 08-05-2023.
//

#ifndef NILM_INDUSTRY_READ_EQ_H
#define NILM_INDUSTRY_READ_EQ_H

#include <string>
#include <vector>

#include "../../estimation/handle_data/Read.h"

class Read_Eq : public Read {
public:
    Read_Eq(const std::string& name_file);

    std::vector<float> get_eq(const int eq_idx) const;
    std::vector<std::vector<float>> get_eqs() const;
private:
    std::vector<std::vector<float>> actual_eq;
};


#endif //NILM_INDUSTRY_READ_EQ_H
