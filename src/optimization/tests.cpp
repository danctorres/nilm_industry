// Unit tests. Run: ctest --test-dir build, or ./tests for doctest's options (-tc=csv, -s, --help).
// Test case names must not contain ";" (CMake splits them when registering with ctest).
#include <doctest/doctest.h>

#include <cmath>
#include <cstdint>
#include <filesystem>
#include <format>
#include <fstream>
#include <random>
#include <stdexcept>
#include <system_error>
#include <vector>

#include "aco.h"
#include "ga.h"
#include "gradient.h"
#include "io.h"
#include "model.h"
#include "pso.h"
#include "sa.h"

using namespace nilm;

namespace {
doctest::Approx approx(double v) {
    return doctest::Approx(v).epsilon(1e-9);
}
}  // namespace

// Horner form equals the explicit cubic; coefs_of picks the right machine
TEST_CASE("poly and coefs_of") {
    const std::vector<double> c = {1.0, 2.0, 3.0, 4.0, 0.5, 0.0, 0.0, 0.0};
    CHECK(poly(coefs_of(c, 0), 2.0) == approx(1 + 2 * 2 + 3 * 4 + 4 * 8));
    CHECK(poly(coefs_of(c, 1), 7.0) == approx(0.5));
}

// exact reconstruction scores 0, an off machine drops out, negative power is penalised
TEST_CASE("objective") {
    const std::vector<int> both{1, 1}, first{1, 0};
    const std::vector<double> half = {0, 0.5, 0, 0, 0, 0.5, 0, 0};  // each machine draws half the aggregate
    CHECK(objective(half, {10.0, both}, 1.0) == approx(0.0));
    CHECK(objective(half, {10.0, first}, 1.0) == approx(25.0));  // residual 10 - 5
    const std::vector<double> neg = {-1.0, 0, 0, 0, 0, 0, 0, 0};
    CHECK(objective(neg, {0.0, first}, 1.0) == approx(1.0 + 6.25));
    CHECK(objective(neg, {0.0, first}, 0.0) == approx(1.0));
}

// perfect prediction, a hand-computed case, constant actual
TEST_CASE("metrics") {
    const std::vector<double> a = {1, 2, 3}, flat = {2, 2, 2};
    CHECK(metrics(a, a).r2 == approx(1.0));
    CHECK(metrics(a, a).mae == approx(0.0));
    const Metrics m = metrics(flat, a);  // errors -1, 0, 1 against actual 1, 2, 3
    CHECK(m.mae == approx(2.0 / 3));
    CHECK(m.mse == approx(2.0 / 3));
    CHECK(m.rmse == approx(std::sqrt(2.0 / 3)));
    CHECK(m.r2 == approx(0.0));
    CHECK(std::isnan(metrics(a, flat).r2));
}

// coefficients fitted on agg/scale reproduce scale * q(agg/scale) in physical units
TEST_CASE("scaling") {
    const std::vector<double> q = {0.1, 0.2, 0.3, 0.4};
    CHECK(poly(unscale(q, 10.0), 7.0) == approx(10.0 * poly(q, 0.7)));
    CHECK(scale_of(std::vector<double>{-3.0, 2.0}) == approx(3.0));
    CHECK(scale_of(std::vector<double>{0.0, 0.0}) == approx(1.0));
}

// per machine over the samples it was on; empty positions (skipped samples) are ignored
TEST_CASE("average_on") {
    const std::vector<std::vector<double>> positions = {{1, 2, 3, 4, 9, 9, 9, 9}, {3, 4, 5, 6, 1, 1, 1, 1}, {}};
    const std::vector<std::vector<int>> states = {{1, 0}, {1, 1}, {1, 1}};
    CHECK(average_on(positions, states, 2) == std::vector<double>{2, 3, 4, 5, 1, 1, 1, 1});
}

// every optimizer finds the minimum of a shifted sphere and is deterministic for a fixed seed
TEST_CASE("optimizers") {
    const std::vector<double> lo(3, -5.0), hi(3, 5.0);
    const auto sphere = [](std::span<const double> x) {
        double s = 0.0;
        for (double v : x) s += (v - 1.0) * (v - 1.0);
        return s;
    };
    const auto converges = [](auto&& algo) {
        const Result r1 = algo(42), r2 = algo(42);
        CAPTURE(r1.iterations);
        CHECK(r1.fitness < 1e-4);
        for (double v : r1.position) CHECK(std::abs(v - 1.0) <= 1e-2);
        CHECK(r1.position == r2.position);
        CHECK(r1.iterations == r2.iterations);
    };
    SUBCASE("pso") {
        converges([&](std::uint64_t seed) {
            return pso(sphere, lo, hi, PsoParams{.particles = 50, .max_iter = 300, .threshold = 1e-8}, seed);
        });
    }
    SUBCASE("ga") {
        converges(
            [&](std::uint64_t seed) { return ga(sphere, lo, hi, GaParams{.max_iter = 300, .threshold = 1e-8}, seed); });
    }
    SUBCASE("sa") {
        converges(
            [&](std::uint64_t seed) { return sa(sphere, lo, hi, SaParams{.max_iter = 500, .threshold = 1e-8}, seed); });
    }
    SUBCASE("aco") {
        converges([&](std::uint64_t seed) {
            return aco(sphere, lo, hi, AcoParams{.max_iter = 500, .threshold = 1e-8}, seed);
        });
    }
    SUBCASE("gd") {
        converges(
            [&](std::uint64_t seed) { return gd(sphere, lo, hi, GdParams{.starts = 3, .threshold = 1e-8}, seed); });
    }
    SUBCASE("newton") {
        converges([&](std::uint64_t seed) {
            return newton(sphere, lo, hi, NewtonParams{.starts = 3, .threshold = 1e-8}, seed);
        });
    }
}

// Cholesky solve of a small SPD system, and rejection of an indefinite one
TEST_CASE("solve_spd") {
    CHECK(solve_spd({4, 2, 2, 3}, {2, 1}).value_or(std::vector<double>{}) == std::vector<double>{0.5, 0.0});
    CHECK_FALSE(solve_spd({1, 2, 2, 1}, {1, 1}).has_value());
}

// header, CRLF, blank trailing lines, spaces around cells, coefficient round trip, bad input
TEST_CASE("csv") {
    struct TempDir {
        std::filesystem::path path =
            std::filesystem::temp_directory_path() / std::format("nilm_tests_{}", std::random_device{}());
        TempDir() { std::filesystem::create_directories(path); }
        ~TempDir() {
            std::error_code ec;
            std::filesystem::remove_all(path, ec);
        }
    } tmp;
    const auto& dir = tmp.path;

    std::ofstream(dir / "agg.csv")
        << "Timestamp, Active power\r\n24-Oct-2017 10:34:08, 1.5\r\n24-Oct-2017 10:34:09, 2.5\r\n\r\n";
    std::ofstream(dir / "st.csv") << "Timestamp,m0,m1\n24-Oct-2017 10:34:08,1,0\n24-Oct-2017 10:34:09,1,1\n";
    const Dataset d = load_dataset(dir / "agg.csv", dir / "st.csv");
    REQUIRE(d.size() == 2);
    REQUIRE(d.machines() == 2);
    CHECK(d.timestamps[0] == "24-Oct-2017 10:34:08");
    CHECK(d.aggregate[1] == approx(2.5));
    CHECK(d.states[0] == std::vector<int>{1, 0});
    CHECK(d.states[1] == std::vector<int>{1, 1});

    const std::vector<double> c = {1.0, 2.0, 3.0, 4.0, 0.5, 0.0, 0.0, 0.0};
    write_coefs(dir / "coef.csv", c);
    CHECK(read_coefs(dir / "coef.csv") == c);

    std::ofstream(dir / "ragged.csv") << "Timestamp,m0,m1\n24-Oct-2017 10:34:08,1,0\n24-Oct-2017 10:34:09,1\n";
    CHECK_THROWS_AS(read_csv(dir / "ragged.csv"), std::runtime_error);
    CHECK_THROWS_AS(to_double("nan"), std::runtime_error);
    CHECK_THROWS_AS(to_double("inf"), std::runtime_error);
    CHECK_THROWS_AS(to_double("1,5"), std::runtime_error);
}
