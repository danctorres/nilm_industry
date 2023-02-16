//
// Created by dtorres on 3/1/23.
//

#ifndef DISSERTATION_NILM_READ_H
#define DISSERTATION_NILM_READ_H

#include <algorithm>
#include <string>

class Read{
public:
    Read();    // constructor

    void read_file(std::string name_file);

    // setters
    void set_timestamp(std::vector<int> &timestamp);
    void set_active_power(std::vector<int> &active_power);
    void set_reactive_power(std::vector<int> &reactive_power);
    void set_apparent_power(std::vector<int> &apparent_power);
    void set_current( std::vector<int> &current);
    void set_voltage(std::vector<int> &voltage);
    void set_power_factor(std::vector<int> &power_factor);

    void add_timestamp(int timestamp);
    void add_active_power(int active_power);
    void add_reactive_power(int reactive_power);
    void add_current(int current);
    void add_voltage(const int voltage);
    void add_power_factor(int power_factor);

    // getters
    std::vector<int> get_parameter(const std::string &name_parameter) const;

    void print_parameter(const std::vector<int> &parameter) const;
    ~Read();
private:
    std::vector<int> timestamp;
    std::vector<int> active_power;
    std::vector<int> reactive_power;
    std::vector<int> apparent_power;
    std::vector<int> current;
    std::vector<int> voltage;
    std::vector<int> power_factor;
};

#endif //DISSERTATION_NILM_READ_H
