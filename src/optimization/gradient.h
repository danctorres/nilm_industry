#pragma once
// Gradient-based local methods from several random starts, with finite-difference derivatives:
// gradient descent with Armijo backtracking, and damped Newton (Levenberg-Marquardt).
// Steps are projected back into [lo, hi]. A pure Newton step is not defined for
// the EMUPF objective: one squared residual gives a rank-one Hessian, so a
// damping term mu*I is required.
#include "optimizer.h"

namespace nilm {

struct GdParams {
    int starts = 20;
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    double step = 1.0;        // length of the first trial move in parameter space, halved until Armijo holds
    double fd_frac = 1e-6;    // finite-difference step as a fraction of the search range
};

struct NewtonParams {
    int starts = 20;
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    double damping = 1e-3;    // initial mu, adapted per start
    double fd_frac = 1e-4;
};

namespace detail {
struct Start {
    std::vector<double> x;
    double fit;
    double mu;
};
template <Objective F>
std::vector<Start> starts(F& f, std::mt19937_64& rng, int n, std::span<const double> lo, std::span<const double> hi, double mu, Result& best) {
    std::vector<Start> out(static_cast<std::size_t>(n));
    for (auto& s : out) {
        s.x = random_point(rng, lo, hi);
        s.fit = f(std::span<const double>(s.x));
        s.mu = mu;
        best.offer(s.x, s.fit);
    }
    return out;
}
inline std::vector<double> fd_steps(std::span<const double> lo, std::span<const double> hi, double frac) {
    std::vector<double> h(lo.size());
    for (std::size_t k = 0; k < h.size(); ++k) h[k] = frac * (hi[k] - lo[k]);
    return h;
}
}  // namespace detail

template <Objective F>
[[nodiscard]] Result gd(F&& f, std::span<const double> lo, std::span<const double> hi, const GdParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    std::mt19937_64 rng(seed);
    Result best;
    auto pts = detail::starts(f, rng, p.starts, lo, hi, 0.0, best);
    const auto h = detail::fd_steps(lo, hi, p.fd_frac);

    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        for (auto& pt : pts) {
            const auto g = gradient(f, pt.x, h);
            double gg = 0.0;
            for (double v : g) gg += v * v;
            if (gg == 0.0) continue;
            double eta = p.step / std::sqrt(gg);  // independent of the objective's scale
            for (int bt = 0; bt < 60; ++bt, eta /= 2) {
                std::vector<double> y(dim);
                for (std::size_t k = 0; k < dim; ++k) y[k] = std::clamp(pt.x[k] - eta * g[k], lo[k], hi[k]);
                const double fy = f(std::span<const double>(y));
                if (fy <= pt.fit - 1e-4 * eta * gg) {
                    pt.x = std::move(y);
                    pt.fit = fy;
                    best.offer(pt.x, pt.fit);
                    break;
                }
            }
        }
        best.iterations = it + 1;
        if (stop.done(best.fitness)) break;
    }
    return best;
}

template <Objective F>
[[nodiscard]] Result newton(F&& f, std::span<const double> lo, std::span<const double> hi, const NewtonParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    std::mt19937_64 rng(seed);
    Result best;
    auto pts = detail::starts(f, rng, p.starts, lo, hi, p.damping, best);
    const auto h = detail::fd_steps(lo, hi, p.fd_frac);

    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        for (auto& pt : pts) {
            const auto g = gradient(f, pt.x, h);
            auto H = hessian(f, pt.x, h);
            for (int tries = 0; tries < 30; ++tries) {
                auto A = H;
                for (std::size_t k = 0; k < dim; ++k) A[k * dim + k] += pt.mu;
                const auto d = solve_spd(std::move(A), g);
                if (!d) {
                    pt.mu *= 10;
                    continue;
                }
                std::vector<double> y(dim);
                for (std::size_t k = 0; k < dim; ++k) y[k] = std::clamp(pt.x[k] - (*d)[k], lo[k], hi[k]);
                const double fy = f(std::span<const double>(y));
                if (fy < pt.fit) {
                    pt.x = std::move(y);
                    pt.fit = fy;
                    pt.mu = std::max(pt.mu / 3, 1e-12);
                    best.offer(pt.x, pt.fit);
                    break;
                }
                pt.mu *= 3;
            }
        }
        best.iterations = it + 1;
        if (stop.done(best.fitness)) break;
    }
    return best;
}

}  // namespace nilm
