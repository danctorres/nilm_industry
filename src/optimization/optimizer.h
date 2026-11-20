#pragma once
// Pieces shared by all optimizers: result type, stopping rule, random numbers,
// finite-difference derivatives and a small SPD linear solver.
// Every optimizer has the signature
//     Result algo(F&& f, std::span<const double> lo, std::span<const double> hi, const Params& p, std::uint64_t seed)
// where f is a callable taking std::span<const double>. Positions stay inside
// the box [lo, hi], and the result is deterministic for a given seed.
#include <algorithm>
#include <cmath>
#include <concepts>
#include <cstdint>
#include <limits>
#include <optional>
#include <random>
#include <span>
#include <vector>

namespace nilm {

template <class F>
concept Objective = std::invocable<F&, std::span<const double>>;

struct Result {
    std::vector<double> position;
    double fitness = std::numeric_limits<double>::infinity();
    int iterations = 0;
    std::uint64_t evaluations = 0;  // filled in by the caller that wraps f

    void offer(std::span<const double> x, double fit) {
        if (fit < fitness) {
            position.assign(x.begin(), x.end());
            fitness = fit;
        }
    }
};

// Stop once the best fitness is below `threshold`, or after `patience`
// iterations without improvement while below 10x threshold.
struct Stopper {
    double threshold;
    int patience = 10;
    int stale = 0;
    double last = std::numeric_limits<double>::infinity();

    bool done(double best) {
        if (best < threshold) return true;
        stale = best < last ? 0 : stale + 1;
        last = std::min(last, best);
        return stale >= patience && best < 10 * threshold;
    }
};

// Uniform in [0, 1). Several times faster than std::uniform_real_distribution.
inline double unit01(std::mt19937_64& rng) { return static_cast<double>(rng() >> 11) * 0x1.0p-53; }

inline std::vector<double> random_point(std::mt19937_64& rng, std::span<const double> lo, std::span<const double> hi) {
    std::vector<double> x(lo.size());
    for (std::size_t k = 0; k < x.size(); ++k) x[k] = std::lerp(lo[k], hi[k], unit01(rng));
    return x;
}

inline void clamp_to(std::vector<double>& x, std::span<const double> lo, std::span<const double> hi) {
    for (std::size_t k = 0; k < x.size(); ++k) x[k] = std::clamp(x[k], lo[k], hi[k]);
}

// Central-difference gradient with per-dimension step h.
template <Objective F>
std::vector<double> gradient(F& f, std::vector<double> x, std::span<const double> h) {
    std::vector<double> g(x.size());
    for (std::size_t k = 0; k < x.size(); ++k) {
        const double x0 = x[k];
        x[k] = x0 + h[k];
        const double fp = f(std::span<const double>(x));
        x[k] = x0 - h[k];
        const double fm = f(std::span<const double>(x));
        x[k] = x0;
        g[k] = (fp - fm) / (2 * h[k]);
    }
    return g;
}

// Central-difference Hessian, row-major n x n, symmetric.
template <Objective F>
std::vector<double> hessian(F& f, std::vector<double> x, std::span<const double> h) {
    const std::size_t n = x.size();
    std::vector<double> H(n * n);
    const double f0 = f(std::span<const double>(x));
    const auto at = [&](std::size_t i, double di, std::size_t j, double dj) {
        x[i] += di;
        x[j] += dj;
        const double v = f(std::span<const double>(x));
        x[i] -= di;
        x[j] -= dj;
        return v;
    };
    for (std::size_t i = 0; i < n; ++i) {
        H[i * n + i] = (at(i, h[i], i, 0.0) - 2 * f0 + at(i, -h[i], i, 0.0)) / (h[i] * h[i]);
        for (std::size_t j = i + 1; j < n; ++j)
            H[i * n + j] = H[j * n + i] = (at(i, h[i], j, h[j]) - at(i, h[i], j, -h[j]) - at(i, -h[i], j, h[j]) +
                                           at(i, -h[i], j, -h[j])) /
                                          (4 * h[i] * h[j]);
    }
    return H;
}

// Solves A d = g for a symmetric positive definite A (row-major) by Cholesky. Empty if A is not SPD.
[[nodiscard]] inline std::optional<std::vector<double>> solve_spd(std::vector<double> A, std::vector<double> g) {
    const std::size_t n = g.size();
    for (std::size_t j = 0; j < n; ++j) {
        double s = A[j * n + j];
        for (std::size_t k = 0; k < j; ++k) s -= A[j * n + k] * A[j * n + k];
        if (!(s > 0.0)) return std::nullopt;
        A[j * n + j] = std::sqrt(s);
        for (std::size_t i = j + 1; i < n; ++i) {
            double t = A[i * n + j];
            for (std::size_t k = 0; k < j; ++k) t -= A[i * n + k] * A[j * n + k];
            A[i * n + j] = t / A[j * n + j];
        }
    }
    for (std::size_t i = 0; i < n; ++i) {  // L y = g
        for (std::size_t k = 0; k < i; ++k) g[i] -= A[i * n + k] * g[k];
        g[i] /= A[i * n + i];
    }
    for (std::size_t i = n; i-- > 0;) {  // L^T d = y
        for (std::size_t k = i + 1; k < n; ++k) g[i] -= A[k * n + i] * g[k];
        g[i] /= A[i * n + i];
    }
    return g;
}

}  // namespace nilm
