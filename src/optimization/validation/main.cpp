//
// Created by danctorres on 05/08/2023.
//


#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include "read_data/Read_Coef.h"
#include "../estimation/read_data/Read_Aggregate.h"
#include "../estimation/read_data/Read_State.h"
#include "read_data/Read_Eq.h"
#include "polynomial_function/polynomial_function.h"
#include "estimations/Estimations.h"
#include "error/Error.h"


int main() {
    auto est_coef = std::make_unique<Read_Coef> ("../../../../results/estimation/estimated_coef.csv");
    auto agg_val = std::make_unique<Read_Aggregate> ("../../../../data/processed/data_6_equipment/aggregate_validation.csv");
    std::vector<float> agg_vec = agg_val->get_parameters("Active power");
    auto st_val = std::make_unique<Read_State>("../../../../data/processed/data_6_equipment/on_off_validation.csv");
    auto eq_val = std::make_unique<Read_Eq> ("../../../../data/processed/data_6_equipment/equipment_validation.csv");

    auto est = std::make_unique<Estimations>();

    auto buff = est_coef->get_coef_eq(0);

    // Normalize agg_vector
    /*auto max_agg = std::max_element(agg_vec.begin(), agg_vec.end());
    auto min_agg = std::min_element(agg_vec.begin(), agg_vec.end());
    for (auto& elem : agg_vec) {
        elem = (elem - *min_agg) / (*max_agg - *min_agg);
    }*/

    for (int i = 0; i < agg_vec.size(); i++) {
        for (int j = 0; j < 6; j++) {
            // std::cout << "pol: " << pol_func(agg_vec[i],st_val->get_one_parameter(j, i), est_coef->get_coef_eq(j)) << std::endl;

            est->set_est(pol_func(agg_vec[i],
                                            st_val->get_one_parameter(j, i),
                                            est_coef->get_coef_eq(j)),
                         j);
        }
    }

    //est->denormalize_all();

    auto error_eq0 = std::make_unique<Error>(est->get_eq(0), eq_val->get_eq(0));
    auto error_eq1 = std::make_unique<Error>(est->get_eq(1), eq_val->get_eq(1));
    auto error_eq2 = std::make_unique<Error>(est->get_eq(2), eq_val->get_eq(2));
    auto error_eq3 = std::make_unique<Error>(est->get_eq(3), eq_val->get_eq(3));
    auto error_eq4 = std::make_unique<Error>(est->get_eq(4), eq_val->get_eq(4));
    auto error_eq5 = std::make_unique<Error>(est->get_eq(5), eq_val->get_eq(5));

    std::cout << "MAE eq0: " << error_eq0->get_mae() << std::endl;
    std::cout << "MAE eq1: " << error_eq1->get_mae() << std::endl;
    std::cout << "MAE eq2: " << error_eq2->get_mae() << std::endl;
    std::cout << "MAE eq3: " << error_eq3->get_mae() << std::endl;
    std::cout << "MAE eq4: " << error_eq4->get_mae() << std::endl;
    std::cout << "MAE eq5: " << error_eq5->get_mae() << std::endl;

    return 0;
}
