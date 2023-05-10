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
        outfile << "Timestamp, Aggregate_Active_Power, Estimate_0, Estimate_1, Estimate_2, Estimate_3, Estimate_4, Estimate_5" << "\n";

        for(int i = 0; i < agg_vec.size(); i++) {
            outfile << timestamp_vec[i] << ", " << agg_vec[i] << ", " << est.get_eq(0)[i] << ", " << est.get_eq(1)[i] <<
            ", " << est.get_eq(2)[i] << ", " << est.get_eq(3)[i] << ", " << est.get_eq(4)[i] << ", " << est.get_eq(5)[i]
            << "\n";
        }
        outfile.close();
    }
    else {
        std::cout << "Error saving into file." << std::endl;
    }
}
