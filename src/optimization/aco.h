#pragma once
// Ant colony optimisation for continuous domains (ACOR, Socha & Dorigo 2008):
// a sorted archive of solutions defines a Gaussian kernel per dimension; each
// ant picks one archive solution by rank weight and samples around it.
#include "optimizer.h"

namespace nilm {

struct AcoParams {
    int archive = 50;  // solutions kept (k)
    int ants = 2;      // new solutions per iteration (m)
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    double q = 1e-4;   // locality of search: small favours the best solutions
    double xi = 0.85;  // width multiplier, the analogue of pheromone evaporation
};

template <Objective F>
[[nodiscard]] Result aco(F&& f, std::span<const double> lo, std::span<const double> hi, const AcoParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    const std::size_t k = static_cast<std::size_t>(std::max(p.archive, 2));
    std::mt19937_64 rng(seed);
    std::normal_distribution<double> gauss(0.0, 1.0);

    struct Sol {
        std::vector<double> x;
        double fit;
    };
    const auto by_fit = [](const Sol& a, const Sol& b) { return a.fit < b.fit; };
    std::vector<Sol> archive(k);
    for (auto& s : archive) {
        s.x = random_point(rng, lo, hi);
        s.fit = f(std::span<const double>(s.x));
    }
    std::sort(archive.begin(), archive.end(), by_fit);
    Result best;
    best.offer(archive.front().x, archive.front().fit);

    std::vector<double> w(k);  // rank weights, best solution first
    for (std::size_t l = 0; l < k; ++l) w[l] = std::exp(-double(l * l) / (2 * p.q * p.q * double(k * k)));
    std::discrete_distribution<std::size_t> choose(w.begin(), w.end());

    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        for (int a = 0; a < p.ants; ++a) {
            const std::size_t l = choose(rng);
            std::vector<double> x(dim);
            for (std::size_t d = 0; d < dim; ++d) {
                double sigma = 0.0;
                for (std::size_t e = 0; e < k; ++e) sigma += std::abs(archive[e].x[d] - archive[l].x[d]);
                sigma *= p.xi / double(k - 1);
                x[d] = std::clamp(archive[l].x[d] + sigma * gauss(rng), lo[d], hi[d]);
            }
            const double fit = f(std::span<const double>(x));
            archive.push_back({std::move(x), fit});
        }
        std::sort(archive.begin(), archive.end(), by_fit);
        archive.resize(k);
        best.offer(archive.front().x, archive.front().fit);
        best.iterations = it + 1;
        if (stop.done(best.fitness)) break;
    }
    return best;
}

}  // namespace nilm
