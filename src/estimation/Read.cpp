//
// Created by dtorres on 3/1/23.
//

#include "Read.h"
#include <iostream>
#include <fstream>
#include <sstream>

void Read::set_data(std::string name_file){
    std::fstream fin;
    fin.open(name_file, std::ios::in);

    if (!fin){
        std::cerr << "Could not open the file!" << std::endl;
        throw;
    }
    else{
        std::vector<std::vector<std::string>> content;
        std::vector<std::string> row;
        std::string line, word;

        std::cout << "Reading -> " << name_file << std::endl;
        while(!fin.eof()){
            row.clear();
            getline(fin, line);
            std::stringstream s(line);
            while(getline(s, word, ',')){
                row.push_back(word);
            }
            content.push_back(row);
        }
        std::cout << "Read -> " << name_file << std::endl;
        fin.close();
        input_data = content;
    }
}

void Read::print_file() {
    for (std::vector<std::string> r : this->input_data) {
        for (std::string w: r) {
            std::cout << "value w: " << w << std::endl;
        }
    }
}

std::vector <std::vector<std::string>> Read::get_data() const {
    return input_data;
}

void Read::print_parameter(const std::vector<int> &parameter) const {
    for (int values: parameter){
        std::cout << values << std::endl;
    }
}


Read::~Read() {
    std::cout << "Parent destructor" << std::endl;
}
