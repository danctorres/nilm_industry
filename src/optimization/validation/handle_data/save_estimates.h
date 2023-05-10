//
// Created by danctorres on 10-05-2023.
//

#ifndef NILM_INDUSTRY_SAVE_ESTIMATES_H
#define NILM_INDUSTRY_SAVE_ESTIMATES_H


#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include "../../estimation/handle_data/Read_Aggregate.h"
#include "../estimations/Estimations.h"

void save_estimates(const std::string name, const Estimations &est, const Read_Aggregate &agg_val);

#endif //NILM_INDUSTRY_SAVE_ESTIMATES_H
