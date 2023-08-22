//
// Created by danctorres on 10-05-2023.
//

#include "save_coef.h"

void save_coef(const std::string name, const double *new_coef, const int *num_ON, const int number_equipment, const double factor_round) {
    std::ofstream outfile(name);
    if (outfile.is_open()) {
        outfile << "Coef 0, Coef 1, Coef 2, Coef 3" << "\n";
        for(int i = 0; i < number_equipment; i++) {
            outfile << std::round((new_coef[i * 3] / num_ON[i]) * factor_round) / factor_round << ", " <<
             std::round((new_coef[i * 3 + 1] / num_ON[i]) * factor_round) / factor_round << ", " <<
             std::round((new_coef[i * 3 + 2] / num_ON[i]) * factor_round) / factor_round << ", " <<
             std::round((new_coef[i * 3 + 3] / num_ON[i]) * factor_round) / factor_round << "\n";
        }
        outfile.close();
    }
    else {
        std::cout << "Error saving into file." << std::endl;
    }
}
