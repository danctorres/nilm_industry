//
// Created by danctorres on 5/8/2023.
//

#ifndef DISSERTATION_NILM_READ_COEF_H
#define DISSERTATION_NILM_READ_COEF_H

#include <iostream>
#include <string>
#include <vector>
#include "../../estimation/handle_data/Read.h"


class Read_Coef : public Read {
public:
    Read_Coef(const std::string& name_file);
    std::vector<float> get_coef_eq(const int eq_idx) const;
private:
    std::vector<float> coef_0;
    std::vector<float> coef_1;
    std::vector<float> coef_2;
};

#endif //DISSERTATION_NILM_READ_COEF_H
