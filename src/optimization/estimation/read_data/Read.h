//
// Created by danctorres on 3/1/23.
//

#ifndef DISSERTATION_NILM_READ_H
#define DISSERTATION_NILM_READ_H

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>


class Read {
public:
    Read();
    Read(const std::string& name_file);
    std::vector<std::vector<std::string>> get_data() const;

    template<typename T>
    void print_parameter(const std::vector<T>& vec) const {
        for (const auto& elem : vec){
            std::cout << elem << std::endl;
        }
    }
    void print_file() const;
private:
    std::vector<std::vector<std::string>> data;
};

#endif //DISSERTATION_NILM_READ_H
