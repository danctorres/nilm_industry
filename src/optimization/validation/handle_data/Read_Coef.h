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
    std::vector<double> get_coef_eq(const int eq_idx) const;
private:
    std::vector<double> coef_0;
    std::vector<double> coef_1;
    std::vector<double> coef_2;
};

#endif //DISSERTATION_NILM_READ_COEF_H
