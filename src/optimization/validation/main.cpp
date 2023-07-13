//
// Created by danctorres on 05/08/2023.
//


#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include "handle_data/Read_Coef.h"
#include "../estimation/handle_data/Read_Aggregate.h"
#include "../estimation/handle_data/Read_State.h"
#include "handle_data/Read_Eq.h"
#include "polynomial_function/polynomial_function.h"
#include "estimations/Estimations.h"
#include "error/Error.h"
#include "handle_data/save_estimates.h"


int main() {
    std::unique_ptr<Read_Coef> est_coef = std::make_unique<Read_Coef> ("../../../../results/optimization/IMDELD/estimated_coef.csv");
    std::unique_ptr<Read_Aggregate>  agg_val = std::make_unique<Read_Aggregate> ("../../../../data/processed/IMDELD/data_6_equipment/aggregate_validation.csv");
    std::unique_ptr<Read_State> st_val = std::make_unique<Read_State>("../../../../data/processed/IMDELD/data_6_equipment/on_off_validation.csv");
    std::unique_ptr<Read_Eq>  eq_val = std::make_unique<Read_Eq> ("../../../../data/processed/IMDELD/data_6_equipment/equipment_validation.csv");

    std::vector<float> agg_vec;
    auto agg_variant = agg_val->get_parameters ("Active power");
    if (auto parameters = std::get_if<std::vector<float>>(&agg_variant)) {
        agg_vec = *parameters;
    }

    std::unique_ptr<Estimations> est = std::make_unique<Estimations>();

    /*
    // Normalize agg_vector
    double min_agg = *std::min_element(agg_vec.begin(), agg_vec.end());
    double max_agg = *std::max_element(agg_vec.begin(), agg_vec.end());

    // float max_agg = 400000.0f;
    // float min_agg = 0.0f;

    for (int i = 0; i < agg_vec.size(); i++) {
        agg_vec[i] = (agg_vec[i] - min_agg) / (max_agg - min_agg);
    }
    */
    std::vector<double> min_eq = {10.0, 10.0, 10.0, 10.0, 10.0, 10.0};
    std::vector<double> max_eq = {2000.0, 2000.0, 5000.0, 10000.0, 1000000.0, 1000000.0};
    est->set_min_max_eq(min_eq, max_eq);

    for (int i = 0; i < agg_vec.size(); i++) {
        for (int j = 0; j < 6; j++) {
            /*std::cout << " pol: " << pol_func(agg_vec[i],
                                              st_val->get_one_parameter(j, i),
                                              est_coef->get_coef_eq(j)) << " st: " << st_val->get_one_parameter(j, i) << std::endl;*/
            est->set_est(pol_func(agg_vec[i],
                                            st_val->get_one_parameter(j, i),
                                            est_coef->get_coef_eq(j)),
                         j);
        }
    }

    /*
    //est->denormalize_all_specific();
    est->denormalize_all(min_agg, max_agg);
    */
    save_estimates("../../../../results/optimization/IMDELD/estimated_active_power.csv", *est, *agg_val);

    auto error_eq0 = std::make_unique<Error>(est->get_eq(0), eq_val->get_eq(0));
    auto error_eq1 = std::make_unique<Error>(est->get_eq(1), eq_val->get_eq(1));
    auto error_eq2 = std::make_unique<Error>(est->get_eq(2), eq_val->get_eq(2));
    auto error_eq3 = std::make_unique<Error>(est->get_eq(3), eq_val->get_eq(3));
    auto error_eq4 = std::make_unique<Error>(est->get_eq(4), eq_val->get_eq(4));
    auto error_eq5 = std::make_unique<Error>(est->get_eq(5), eq_val->get_eq(5));

    std::cout << "MAE: " << error_eq0->get_mae() << "  " << error_eq1->get_mae() << " " << error_eq2->get_mae()
    << " " << error_eq3->get_mae() << " " << error_eq4->get_mae() << " " << error_eq5->get_mae() << std::endl;
    std::cout << "MSE: " << error_eq0->get_mse() << "  " << error_eq1->get_mse() << " " << error_eq2->get_mse()
              << " " << error_eq3->get_mse() << " " << error_eq4->get_mse() << " " << error_eq5->get_mse() << std::endl;
    std::cout << "RMSE: " << error_eq0->get_rmse() << "  " << error_eq1->get_rmse() << " " << error_eq2->get_rmse()
              << " " << error_eq3->get_rmse() << " " << error_eq4->get_rmse() << " " << error_eq5->get_rmse() << std::endl;
    std::cout << "R2: " << error_eq0->get_r2() << "  " << error_eq1->get_r2() << " " << error_eq2->get_r2()
              << " " << error_eq3->get_r2() << " " << error_eq4->get_r2() << " " << error_eq5->get_r2() << std::endl;

    return 0;
}
