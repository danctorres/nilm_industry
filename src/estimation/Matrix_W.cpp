//
// Created by dtorres on 3/11/23.
//

#include "Matrix_W.h"
#include <vector>

std::vector<std::vector<int>> Matrix_W::get_coefficients(int equipment_number) {
    if (equipment_number == 0){
        return coef_0;
    }
    if (equipment_number == 1){
        return coef_1;
    }
    if (equipment_number == 2){
        return coef_2;
    }
    if (equipment_number == 3){
        return coef_3;
    }
    if (equipment_number == 4){
        return coef_4;
    }
    if (equipment_number == 5){
        return coef_5;
    }
    if (equipment_number == 6){
        return coef_6;
    }
    if (equipment_number == 7){
        return coef_7;
    }
    else{
        throw;
    }
}
