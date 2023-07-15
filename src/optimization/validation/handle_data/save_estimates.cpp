//
// Created by danctorres on 10-05-2023.
//

#include "save_estimates.h"

void save_estimates(const std::string name, const Estimations &est, const Read_Aggregate &agg_val) {
    std::vector<float> agg_vec;
    std::vector<std::string> timestamp_vec;
    auto agg_variant = agg_val.get_parameters("Active power");
    if (auto parameters = std::get_if<std::vector<float>>(&agg_variant)) {
        agg_vec = *parameters;
    }
    auto timestamp_variant = agg_val.get_parameters ("Timestamp");
    if (auto parameters = std::get_if<std::vector<std::string>>(&timestamp_variant)) {
        timestamp_vec = *parameters;
    }
    std::ofstream outfile(name);

    if (outfile.is_open()) {
        outfile << "Timestamp, Aggregate_Active_Power, Estimates" << "\n";

        int number_equipment = est.get_size_equipment();
        for(int i = 0; i < agg_vec.size(); i++) {
            outfile << timestamp_vec[i] << ", " << agg_vec[i] << ", ";
            for(int j = 0; j < number_equipment; j++) {
                if (j == number_equipment - 1) {
                    outfile << est.get_eq(j)[i] << "\n";
                }
                else {
                    outfile << est.get_eq(j)[i] << ", ";
                }
            }
        }
        outfile.close();
    }
    else {
        std::cout << "Error saving into file." << std::endl;
    }
}
