#pragma once
// Simulated annealing: independent chains with Metropolis acceptance, geometric
// cooling and a proposal step that adapts to keep the acceptance rate near 50%.
#include "optimizer.h"

namespace nilm {

struct SaParams {
    int chains = 20;           // independent annealing runs
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    double temperature = 0.0;  // initial; 0 = spread of the initial chains' fitness
    double temp_min = 0.0;     // stop when the temperature falls below this
    double cooling = 0.0;      // temperature multiplier per iteration; 0 = reach `threshold` at max_iter
    double step_frac = 0.1;    // initial proposal step as a fraction of the search range
};

template <Objective F>
[[nodiscard]] Result sa(F&& f, std::span<const double> lo, std::span<const double> hi, const SaParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    std::mt19937_64 rng(seed);

    struct Chain {
        std::vector<double> x;
        double fit;
    };
    std::vector<Chain> chains(static_cast<std::size_t>(p.chains));
    Result best;
    double worst = -std::numeric_limits<double>::infinity();
    for (auto& c : chains) {
        c.x = random_point(rng, lo, hi);
        c.fit = f(std::span<const double>(c.x));
        best.offer(c.x, c.fit);
        worst = std::max(worst, c.fit);
    }
    std::vector<double> step(dim);
    for (std::size_t k = 0; k < dim; ++k) step[k] = p.step_frac * (hi[k] - lo[k]);
    double T = p.temperature > 0 ? p.temperature : std::max(worst - best.fitness, 1e-300);
    const double cooling = p.cooling > 0 ? p.cooling : std::min(1.0, std::pow(std::max(p.threshold, 1e-300) / T, 1.0 / p.max_iter));

    double scale = 1.0;  // step multiplier, grown or shrunk from the acceptance rate
    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        int accepted = 0;
        for (auto& c : chains) {
            std::vector<double> y = c.x;
            for (std::size_t k = 0; k < dim; ++k) y[k] = std::clamp(y[k] + scale * std::lerp(-step[k], step[k], unit01(rng)), lo[k], hi[k]);
            const double fy = f(std::span<const double>(y));
            if (fy < c.fit || unit01(rng) < std::exp(-(fy - c.fit) / T)) {
                c.x = std::move(y);
                c.fit = fy;
                best.offer(c.x, c.fit);
                ++accepted;
            }
        }
        const double rate = static_cast<double>(accepted) / static_cast<double>(chains.size());
        if (rate > 0.6) scale = std::min(scale * 1.5, 1.0 / p.step_frac);  // never beyond the full range
        else if (rate < 0.4) scale *= 0.67;
        T *= cooling;
        best.iterations = it + 1;
        if (T < p.temp_min || stop.done(best.fitness)) break;
    }
    return best;
}

}  // namespace nilm
