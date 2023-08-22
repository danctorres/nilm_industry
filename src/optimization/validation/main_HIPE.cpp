//
// Created by danctorres on 05/08/2023.
//


#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include "../estimation/handle_data/Read_Coef.h"
#include "../estimation/handle_data/Read_Aggregate.h"
#include "../estimation/handle_data/Read_State.h"
#include "handle_data/Read_Eq.h"
#include "../estimation/error/Error.h"
#include "../estimation/polynomial_function/polynomial_function.h"
#include "estimations/Estimations.h"
#include "handle_data/save_estimates.h"


int main() {
    const int number_equipment = 9;
    std::unique_ptr<Read_Coef> est_coef = std::make_unique<Read_Coef> ("../../../../results/optimization/HIPE/1_week/estimated_coef_" + std::to_string(number_equipment) + ".csv");
    std::unique_ptr<Read_Aggregate> agg_val = std::make_unique<Read_Aggregate> ("../../../../data/processed/HIPE/1_week/aggregate_validation/agg_validation_" + std::to_string(number_equipment) + ".csv");
    std::unique_ptr<Read_State> st_val = std::make_unique<Read_State>("../../../../data/processed/HIPE/1_week/state_validation/st_validation_" + std::to_string(number_equipment) + ".csv");
    std::unique_ptr<Read_Eq> eq_val = std::make_unique<Read_Eq> ("../../../../data/processed/HIPE/1_week/equipment_validation/eq_validation_" + std::to_string(number_equipment) + ".csv");

    std::vector<float> agg_vec;
    auto agg_variant = agg_val->get_parameters ("Active power");
    if (auto parameters = std::get_if<std::vector<float>>(&agg_variant)) {
        agg_vec = *parameters;
    }

    std::unique_ptr<Estimations> est = std::make_unique<Estimations>();

    for (int i = 0; i < agg_vec.size(); i++) {
        for (int j = 0; j < number_equipment; j++) {
            est->set_est(pol_func(agg_vec[i],
                                            st_val->get_one_parameter(j, i),
                                            est_coef->get_coef_eq(j)),
                         j);
        }
    }

    save_estimates("../../../../results/optimization/HIPE/1_week/estimated_active_power_" + std::to_string(number_equipment) + ".csv", *est, *agg_val);

    std::vector<std::unique_ptr<Error>> error_eq;
    for (int i = 0; i < number_equipment; i++) {
        error_eq.push_back(std::make_unique<Error>(est->get_eq(i), eq_val->get_eq(i)));
        std::cout << "Eq " << i << " - MAE: "<< error_eq[i]->get_mae() << ", ";
        std::cout << "MSE: "<< error_eq[i]->get_mse() << ", ";
        std::cout << "RMSE: "<< error_eq[i]->get_rmse() << ", ";
        std::cout << "R2: "<< error_eq[i]->get_r2() << std::endl;

    }

    return 0;
}
