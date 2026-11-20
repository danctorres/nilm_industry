// The smallest checks that fail if the logic breaks. Run: ./tests (or ctest).
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <format>
#include <fstream>
#include <iostream>
#include <random>
#include <string_view>
#include <vector>

#include "aco.h"
#include "ga.h"
#include "gradient.h"
#include "io.h"
#include "model.h"
#include "pso.h"
#include "sa.h"

#define CHECK(cond)                                                                        \
    do {                                                                                   \
        if (!(cond)) {                                                                     \
            std::cerr << std::format("{}:{}: CHECK failed: {}\n", __FILE__, __LINE__, #cond); \
            std::exit(1);                                                                  \
        }                                                                                  \
    } while (0)

int main() {
    using namespace nilm;
    const auto near = [](double a, double b, double tol = 1e-9) { return std::abs(a - b) <= tol; };

    // poly: Horner form equals the explicit cubic; coefs_of picks the right machine
    const std::vector<double> c = {1.0, 2.0, 3.0, 4.0, 0.5, 0.0, 0.0, 0.0};
    CHECK(near(poly(coefs_of(c, 0), 2.0), 1 + 2 * 2 + 3 * 4 + 4 * 8));
    CHECK(near(poly(coefs_of(c, 1), 7.0), 0.5));

    // objective: exact reconstruction scores 0, an off machine drops out, negative power is penalised
    const std::vector<int> both{1, 1}, first{1, 0};
    const std::vector<double> half = {0, 0.5, 0, 0, 0, 0.5, 0, 0};  // each machine draws half the aggregate
    CHECK(near(objective(half, {10.0, both}, 1.0), 0.0));
    CHECK(near(objective(half, {10.0, first}, 1.0), 25.0));  // residual 10 - 5
    const std::vector<double> neg = {-1.0, 0, 0, 0, 0, 0, 0, 0};
    CHECK(near(objective(neg, {0.0, first}, 1.0), 1.0 + 6.25));
    CHECK(near(objective(neg, {0.0, first}, 0.0), 1.0));

    // metrics: perfect prediction, a hand-computed case (errors -1, 0, 1 against actual 1, 2, 3), constant actual
    const std::vector<double> a = {1, 2, 3}, flat = {2, 2, 2};
    CHECK(near(metrics(a, a).r2, 1.0) && near(metrics(a, a).mae, 0.0));
    const Metrics m = metrics(flat, a);
    CHECK(near(m.mae, 2.0 / 3) && near(m.mse, 2.0 / 3) && near(m.rmse, std::sqrt(2.0 / 3)) && near(m.r2, 0.0));
    CHECK(std::isnan(metrics(a, flat).r2));

    // scaling: coefficients fitted on agg/scale reproduce scale * q(agg/scale) in physical units
    const std::vector<double> q = {0.1, 0.2, 0.3, 0.4};
    CHECK(near(poly(unscale(q, 10.0), 7.0), 10.0 * poly(q, 0.7), 1e-9));
    CHECK(near(scale_of(std::vector<double>{-3.0, 2.0}), 3.0) && near(scale_of(std::vector<double>{0.0, 0.0}), 1.0));

    // averaging: per machine over the samples it was on; empty positions (skipped samples) are ignored
    const std::vector<std::vector<double>> positions = {{1, 2, 3, 4, 9, 9, 9, 9}, {3, 4, 5, 6, 1, 1, 1, 1}, {}};
    const std::vector<std::vector<int>> states = {{1, 0}, {1, 1}, {1, 1}};
    CHECK((average_on(positions, states, 2) == std::vector<double>{2, 3, 4, 5, 1, 1, 1, 1}));

    // every optimizer finds the minimum of a shifted sphere and is deterministic for a fixed seed
    const std::vector<double> lo(3, -5.0), hi(3, 5.0);
    const auto sphere = [](std::span<const double> x) {
        double s = 0.0;
        for (double v : x) s += (v - 1.0) * (v - 1.0);
        return s;
    };
    const auto converges = [&](std::string_view name, auto&& algo) {
        const Result r1 = algo(42), r2 = algo(42);
        if (!(r1.fitness < 1e-4)) {
            std::cerr << std::format("{}: fitness {} after {} iterations\n", name, r1.fitness, r1.iterations);
            std::exit(1);
        }
        for (double v : r1.position) CHECK(near(v, 1.0, 1e-2));
        CHECK(r1.position == r2.position && r1.iterations == r2.iterations);
    };
    converges("pso", [&](std::uint64_t seed) { PsoParams p; p.particles = 50; p.max_iter = 300; p.threshold = 1e-8; return pso(sphere, lo, hi, p, seed); });
    converges("ga", [&](std::uint64_t seed) { GaParams p; p.max_iter = 300; p.threshold = 1e-8; return ga(sphere, lo, hi, p, seed); });
    converges("sa", [&](std::uint64_t seed) { SaParams p; p.max_iter = 500; p.threshold = 1e-8; return sa(sphere, lo, hi, p, seed); });
    converges("aco", [&](std::uint64_t seed) { AcoParams p; p.max_iter = 500; p.threshold = 1e-8; return aco(sphere, lo, hi, p, seed); });
    converges("gd", [&](std::uint64_t seed) { GdParams p; p.starts = 3; p.threshold = 1e-8; return gd(sphere, lo, hi, p, seed); });
    converges("newton", [&](std::uint64_t seed) { NewtonParams p; p.starts = 3; p.threshold = 1e-8; return newton(sphere, lo, hi, p, seed); });

    // solve_spd: Cholesky solve of a small SPD system, and rejection of an indefinite one
    CHECK((*solve_spd({4, 2, 2, 3}, {2, 1}) == std::vector<double>{0.5, 0.0}));
    CHECK(!solve_spd({1, 2, 2, 1}, {1, 1}));

    // csv: header, CRLF, blank trailing lines, spaces around cells, coefficient round trip
    const auto dir = std::filesystem::temp_directory_path() / std::format("nilm_tests_{}", std::random_device{}());
    std::filesystem::create_directories(dir);
    std::ofstream(dir / "agg.csv") << "Timestamp, Active power\r\n24-Oct-2017 10:34:08, 1.5\r\n24-Oct-2017 10:34:09, 2.5\r\n\r\n";
    std::ofstream(dir / "st.csv") << "Timestamp,m0,m1\n24-Oct-2017 10:34:08,1,0\n24-Oct-2017 10:34:09,1,1\n";
    const Dataset d = load_dataset(dir / "agg.csv", dir / "st.csv");
    CHECK(d.size() == 2 && d.machines() == 2);
    CHECK(d.timestamps[0] == "24-Oct-2017 10:34:08" && near(d.aggregate[1], 2.5));
    CHECK((d.states[0] == std::vector<int>{1, 0} && d.states[1] == std::vector<int>{1, 1}));
    write_coefs(dir / "coef.csv", c);
    CHECK(read_coefs(dir / "coef.csv") == c);
    std::ofstream(dir / "ragged.csv") << "Timestamp,m0,m1\n24-Oct-2017 10:34:08,1,0\n24-Oct-2017 10:34:09,1\n";
    const auto rejects = [](auto&& call) {
        try { call(); } catch (const std::runtime_error&) { return true; }
        return false;
    };
    CHECK(rejects([&] { read_csv(dir / "ragged.csv"); }));
    CHECK(rejects([] { to_double("nan"); }) && rejects([] { to_double("inf"); }) && rejects([] { to_double("1,5"); }));
    std::filesystem::remove_all(dir);

    std::cout << "all checks passed\n";
}
