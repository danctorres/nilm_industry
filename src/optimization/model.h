#pragma once
// EMUPF model: each machine's active power is a cubic polynomial of the aggregate
// power, switched by its on/off state. All coefficients live in one flat vector,
// kCoefs consecutive values per machine.
//
// Fitting works on the aggregate divided by its largest value (`scale_of`), so
// bounds, thresholds and fitness are unit-free; `unscale` converts the fitted
// coefficients back to physical units for the coefficient file.
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <span>
#include <vector>

namespace nilm {

inline constexpr std::size_t kCoefs = 4;

inline double poly(std::span<const double> c, double agg) {
    return c[0] + agg * (c[1] + agg * (c[2] + agg * c[3]));
}

inline std::span<const double> coefs_of(std::span<const double> all, std::size_t machine) {
    return all.subspan(machine * kCoefs, kCoefs);
}

struct Sample {
    double agg;
    std::span<const int> on;
};

inline double estimate(std::span<const double> coefs, std::size_t j, const Sample& s) {
    return s.on[j] != 0 ? poly(coefs_of(coefs, j), s.agg) : 0.0;
}

inline double reconstruct(std::span<const double> coefs, const Sample& s) {
    double sum = 0.0;
    for (std::size_t j = 0; j < s.on.size(); ++j) sum += estimate(coefs, j, s);
    return sum;
}

// Squared reconstruction error plus a quadratic penalty, weighted by lambda,
// for every machine whose estimated power is negative.
inline double objective(std::span<const double> coefs, const Sample& s, double lambda) {
    double sum = 0.0, penalty = 0.0;
    for (std::size_t j = 0; j < s.on.size(); ++j) {
        const double p = estimate(coefs, j, s);
        sum += p;
        if (p < 0.0) penalty += (2.5 * p) * (2.5 * p);
    }
    const double r = s.agg - sum;
    return r * r + lambda * penalty;
}

inline double scale_of(std::span<const double> aggregate) {
    double s = 0.0;
    for (double a : aggregate) s = std::max(s, std::abs(a));
    return s > 0.0 ? s : 1.0;
}

// Coefficients fitted on agg/scale, converted to physical units:
// scale * q(agg/scale) = sum_k (c_k * scale^(1-k)) agg^k.
inline std::vector<double> unscale(std::vector<double> coefs, double scale) {
    for (std::size_t i = 0; i < coefs.size(); ++i) coefs[i] *= std::pow(scale, 1.0 - static_cast<double>(i % kCoefs));
    return coefs;
}

inline std::vector<double> average_on(std::span<const std::vector<double>> positions,
                                      std::span<const std::vector<int>> states, std::size_t machines) {
    std::vector<double> mean(machines * kCoefs, 0.0);
    std::vector<int> count(machines, 0);
    for (std::size_t i = 0; i < positions.size(); ++i) {
        if (positions[i].empty()) continue;
        for (std::size_t j = 0; j < machines; ++j)
            if (states[i][j] != 0) {
                ++count[j];
                for (std::size_t k = 0; k < kCoefs; ++k) mean[j * kCoefs + k] += positions[i][j * kCoefs + k];
            }
    }
    for (std::size_t j = 0; j < machines; ++j)
        if (count[j] != 0)
            for (std::size_t k = 0; k < kCoefs; ++k) mean[j * kCoefs + k] /= count[j];
    return mean;
}

struct Metrics {
    double mae, mse, rmse, r2;  // r2 is NaN when the actual values have no variance
};

inline Metrics metrics(std::span<const double> est, std::span<const double> actual) {
    const auto n = static_cast<double>(actual.size());
    double mean = 0.0;
    for (double a : actual) mean += a / n;
    double abs_err = 0.0, sq_err = 0.0, sq_tot = 0.0;
    for (std::size_t i = 0; i < actual.size(); ++i) {
        const double e = actual[i] - est[i];
        abs_err += std::abs(e);
        sq_err += e * e;
        sq_tot += (actual[i] - mean) * (actual[i] - mean);
    }
    const double r2 = sq_tot > 0.0 ? 1.0 - sq_err / sq_tot : std::numeric_limits<double>::quiet_NaN();
    return {abs_err / n, sq_err / n, std::sqrt(sq_err / n), r2};
}

}  // namespace nilm
