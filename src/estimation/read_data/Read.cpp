//
// Created by dtorres on 3/1/23.
//

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "Read.h"

Read::Read() {}

Read::Read(const std::string& name_file) {
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
        data = content;
    }
}

std::vector <std::vector<std::string>> Read::get_data() const {
    return data;
}

void Read::print_file() const {
    for (const auto& r : this->data) {
        for (auto w: r) {
            std::cout << "value w: " << w << std::endl;
        }
    }
}
