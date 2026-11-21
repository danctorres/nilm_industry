// Applies fitted coefficients to a validation set, writes the per-machine
// estimates and prints MAE, MSE, RMSE and R2 per machine against measured power.
#include <cmath>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "io.h"
#include "model.h"

int main(int argc, char** argv) try {
    if (argc != 6) {
        std::cerr << "usage: validate <aggregate.csv> <states.csv> <equipment.csv> <coef.csv> <out_estimates.csv>\n";
        return 1;
    }
    const nilm::Dataset d = nilm::load_dataset(argv[1], argv[2]);
    const nilm::Table equipment = nilm::read_csv(argv[3]);  // timestamp, then measured power per machine
    const std::vector<double> coefs = nilm::read_coefs(argv[4]);
    const std::size_t m = d.machines();
    if (coefs.size() != m * nilm::kCoefs)
        throw std::runtime_error(
            std::format("{} holds {} machines, states hold {}", argv[4], coefs.size() / nilm::kCoefs, m));
    if (equipment.rows.size() != d.size())
        throw std::runtime_error(
            std::format("{} has {} rows, states have {}", argv[3], equipment.rows.size(), d.size()));
    if (equipment.header.size() != m + 1)
        throw std::runtime_error(
            std::format("{} holds {} machines, states hold {}", argv[3], equipment.header.size() - 1, m));

    std::vector<std::vector<double>> est(m, std::vector<double>(d.size()));
    std::vector<std::vector<double>> actual(m, std::vector<double>(d.size()));
    for (std::size_t i = 0; i < d.size(); ++i)
        for (std::size_t j = 0; j < m; ++j) {
            est[j][i] = nilm::estimate(coefs, j, d.sample(i));
            actual[j][i] = nilm::to_double(equipment.rows[i].at(j + 1));
        }
    nilm::write_estimates(argv[5], d, est);

    for (std::size_t j = 0; j < m; ++j) {
        const auto r = nilm::metrics(est[j], actual[j]);
        const std::string r2 = std::isnan(r.r2) ? "n/a (constant actual)" : std::format("{:.4f}", r.r2);
        std::cout << std::format("machine {}: MAE {:.4g}  MSE {:.4g}  RMSE {:.4g}  R2 {}\n", j, r.mae, r.mse, r.rmse,
                                 r2);
    }
    return 0;
} catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
}
