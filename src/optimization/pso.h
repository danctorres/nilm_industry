#pragma once
// Particle swarm optimisation with linearly decreasing inertia weight.
#include "optimizer.h"

namespace nilm {

struct PsoParams {
    int particles = 1000;
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    double c1 = 2.0;          // cognitive weight
    double c2 = 2.0;          // social weight
    double w_max = 0.9;       // inertia decreases linearly from w_max to w_min
    double w_min = 0.4;
    double v_max_frac = 0.2;  // velocity clamp as a fraction of the search range
};

template <Objective F>
[[nodiscard]] Result pso(F&& f, std::span<const double> lo, std::span<const double> hi, const PsoParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    std::mt19937_64 rng(seed);

    std::vector<double> v_max(dim);
    for (std::size_t k = 0; k < dim; ++k) v_max[k] = p.v_max_frac * (hi[k] - lo[k]);

    struct Particle {
        std::vector<double> x, v, best_x;
        double best_fit;
    };
    std::vector<Particle> swarm(static_cast<std::size_t>(p.particles));
    Result best;
    for (auto& q : swarm) {
        q.x = random_point(rng, lo, hi);
        q.v.resize(dim);
        for (std::size_t k = 0; k < dim; ++k) q.v[k] = std::lerp(-v_max[k], v_max[k], unit01(rng));
        q.best_x = q.x;
        q.best_fit = f(std::span<const double>(q.x));
        best.offer(q.x, q.best_fit);
    }

    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        const double w = p.w_max - (p.w_max - p.w_min) * it / p.max_iter;
        for (auto& q : swarm) {
            for (std::size_t k = 0; k < dim; ++k) {
                const double vel = w * q.v[k] + p.c1 * unit01(rng) * (q.best_x[k] - q.x[k]) +
                                   p.c2 * unit01(rng) * (best.position[k] - q.x[k]);
                q.v[k] = std::clamp(vel, -v_max[k], v_max[k]);
                q.x[k] = std::clamp(q.x[k] + q.v[k], lo[k], hi[k]);
            }
            const double fit = f(std::span<const double>(q.x));
            if (fit < q.best_fit) {
                q.best_fit = fit;
                q.best_x = q.x;
                best.offer(q.x, fit);
            }
        }
        best.iterations = it + 1;
        if (stop.done(best.fitness)) break;
    }
    return best;
}

}  // namespace nilm
