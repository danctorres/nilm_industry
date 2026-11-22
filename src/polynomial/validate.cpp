// Applies fitted coefficients to a validation set and writes each machine's estimated power.
// src/validation/validation.py scores them.
#include <format>
#include <iostream>
#include <stdexcept>
#include <vector>

#include "io.h"
#include "model.h"

int main(int argc, char** argv) try {
    if (argc != 5) {
        std::cerr << "usage: validate <aggregate.csv> <states.csv> <coef.csv> <out_estimates.csv>\n";
        return 1;
    }
    const nilm::Dataset d = nilm::load_dataset(argv[1], argv[2]);
    const std::vector<double> coefs = nilm::read_coefs(argv[3]);
    const std::size_t m = d.machines();
    if (coefs.size() != m * nilm::kCoefs)
        throw std::runtime_error(
            std::format("{} holds {} machines, states hold {}", argv[3], coefs.size() / nilm::kCoefs, m));

    std::vector<std::vector<double>> est(m, std::vector<double>(d.size()));
    for (std::size_t i = 0; i < d.size(); ++i)
        for (std::size_t j = 0; j < m; ++j) est[j][i] = nilm::estimate(coefs, j, d.sample(i));
    nilm::write_estimates(argv[4], d, est);
    return 0;
} catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
}
