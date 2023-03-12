//
// Created by dtorres on 3/1/23.
//

#ifndef DISSERTATION_NILM_READ_H
#define DISSERTATION_NILM_READ_H

#include <algorithm>
#include <string>

class Read{
public:
    void set_data(std::string name_file);
    [[nodiscard]] std::vector<std::vector<std::string>> get_data() const;

    [[maybe_unused]] void print_file();
    static void print_parameter(const std::vector<uint_fast32_t> &parameter) ;
    //~Read();
private:
    std::vector<std::vector<std::string>> input_data;
};

#endif //DISSERTATION_NILM_READ_H
