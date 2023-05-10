//
// Created by danctorres on 10-05-2023.
//

#include "save_coef.h"

void save_coef(const std::string name, const float *sum_est, const int *num_ON) {
    std::ofstream outfile(name);
    if (outfile.is_open()) {
        outfile << "Coef 0, Coef 1, Coef 2" << "\n";
        for(int i = 0; i < 6; i++) {
            outfile << sum_est[i * 3] / num_ON[i]  << ", " << sum_est[i * 3 + 1] / num_ON[i] << ", " << sum_est[i * 3 + 2] / num_ON[i] << "\n";
        }
        outfile.close();
    }
    else {
        std::cout << "Error saving into file." << std::endl;
    }
}
