// Fits the EMUPF polynomial coefficients from aggregate power and on/off states.
// Every sample with at least one machine on is an independent optimisation
// problem, solved by the chosen algorithm on the aggregate divided by its
// largest value; the coefficients of the machines that were on are averaged
// over all samples and converted back to physical units. This repeats for
// --cycles random restarts and keeps the coefficient set with the lowest
// reconstruction MAE, also against a coefficient file that already exists.
// With --joint there is one optimisation of the mean per-sample objective over
// all samples instead, and no averaging.
#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <format>
#include <iostream>
#include <limits>
#include <random>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <variant>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

#include "aco.h"
#include "ga.h"
#include "gradient.h"
#include "io.h"
#include "model.h"
#include "pso.h"
#include "sa.h"

namespace {

using Params = std::variant<nilm::PsoParams, nilm::GaParams, nilm::SaParams, nilm::AcoParams, nilm::GdParams, nilm::NewtonParams>;

struct Options {
    std::filesystem::path aggregate, states, out;
    std::string_view algorithm = "pso";
    bool joint = false;  // one optimisation over all samples instead of one per sample
    int cycles = 5;
    int particles = 0;  // population, archive, chains or starts; 0 = the algorithm's default
    int iters = 200;
    double threshold = 1e-5;  // on the normalised objective
    double bound = 1.0;       // coefficients are confined to [-bound, bound], in normalised units
    double lambda = 1.0;      // weight of the negative-power penalty
    std::uint64_t seed = std::random_device{}();
};

constexpr std::string_view kUsage =
    "usage: estimate <aggregate.csv> <states.csv> <out_coef.csv>\n"
    "  [--algorithm pso|ga|sa|aco|gd|newton] [--joint] [--cycles N=5] [--particles N] [--iters N=200]\n"
    "  [--threshold X=1e-5] [--bound X=1] [--lambda X=1] [--seed N]\n"
    "--joint fits one objective (the mean of the per-sample objectives) over all samples.\n"
    "--particles is the population (pso, ga), archive (aco), chains (sa) or starts (gd, newton);\n"
    "omitted or 0 uses the algorithm's default. Set OMP_NUM_THREADS to control parallelism.\n";

int to_int(std::string_view s) {
    int v{};
    const auto [end, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || end != s.data() + s.size()) throw std::runtime_error(std::format("bad integer '{}'", s));
    return v;
}

Options parse(int argc, char** argv) {
    const std::vector<std::string_view> args(argv + 1, argv + argc);
    if (args.size() < 3) throw std::runtime_error(std::string(kUsage));
    Options o;
    o.aggregate = args[0];
    o.states = args[1];
    o.out = args[2];
    for (std::size_t i = 3; i < args.size(); i += 2) {
        if (args[i] == "--joint") {
            o.joint = true;
            --i;
            continue;
        }
        if (i + 1 >= args.size()) throw std::runtime_error(std::format("missing value for {}\n{}", args[i], kUsage));
        const auto flag = args[i], v = args[i + 1];
        if (flag == "--algorithm") o.algorithm = v;
        else if (flag == "--cycles") o.cycles = to_int(v);
        else if (flag == "--particles") o.particles = to_int(v);
        else if (flag == "--iters") o.iters = to_int(v);
        else if (flag == "--threshold") o.threshold = nilm::to_double(v);
        else if (flag == "--bound") o.bound = nilm::to_double(v);
        else if (flag == "--lambda") o.lambda = nilm::to_double(v);
        else if (flag == "--seed") {
            const auto [end, ec] = std::from_chars(v.data(), v.data() + v.size(), o.seed);
            if (ec != std::errc{} || end != v.data() + v.size()) throw std::runtime_error(std::format("bad seed '{}'", v));
        } else throw std::runtime_error(std::format("unknown flag {}\n{}", flag, kUsage));
    }
    if (!(o.bound > 0)) throw std::runtime_error("--bound must be positive");
    if (o.cycles < 1 || o.iters < 1) throw std::runtime_error("--cycles and --iters must be at least 1");
    return o;
}

// The chosen algorithm's parameters: shared knobs from the CLI, the rest from the struct defaults.
Params make_params(const Options& o) {
    const auto with = [&]<class P>(P p, int P::*size) {
        p.max_iter = o.iters;
        p.threshold = o.threshold;
        if (o.particles > 0) p.*size = o.particles;
        return Params{std::move(p)};
    };
    if (o.algorithm == "pso") return with(nilm::PsoParams{}, &nilm::PsoParams::particles);
    if (o.algorithm == "ga") return with(nilm::GaParams{}, &nilm::GaParams::population);
    if (o.algorithm == "sa") return with(nilm::SaParams{}, &nilm::SaParams::chains);
    if (o.algorithm == "aco") return with(nilm::AcoParams{}, &nilm::AcoParams::archive);
    if (o.algorithm == "gd") return with(nilm::GdParams{}, &nilm::GdParams::starts);
    if (o.algorithm == "newton") return with(nilm::NewtonParams{}, &nilm::NewtonParams::starts);
    throw std::runtime_error(std::format("unknown algorithm {}\n{}", o.algorithm, kUsage));
}

using Span = std::span<const double>;
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::PsoParams& p, std::uint64_t s) { return nilm::pso(f, lo, hi, p, s); }
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::GaParams& p, std::uint64_t s) { return nilm::ga(f, lo, hi, p, s); }
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::SaParams& p, std::uint64_t s) { return nilm::sa(f, lo, hi, p, s); }
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::AcoParams& p, std::uint64_t s) { return nilm::aco(f, lo, hi, p, s); }
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::GdParams& p, std::uint64_t s) { return nilm::gd(f, lo, hi, p, s); }
template <class F> nilm::Result run(F& f, Span lo, Span hi, const nilm::NewtonParams& p, std::uint64_t s) { return nilm::newton(f, lo, hi, p, s); }

std::string describe(const nilm::PsoParams& p) {
    return std::format("pso: particles {}, max_iter {}, threshold {}, patience {}, c1 {}, c2 {}, w {}->{}, v_max_frac {}", p.particles,
                       p.max_iter, p.threshold, p.patience, p.c1, p.c2, p.w_max, p.w_min, p.v_max_frac);
}
std::string describe(const nilm::GaParams& p) {
    return std::format("ga: population {}, max_iter {}, threshold {}, patience {}, tournament {}, alpha {}, beta {}, p_mutation {}, mutation_index {}, elite {}",
                       p.population, p.max_iter, p.threshold, p.patience, p.tournament, p.alpha, p.beta, p.p_mutation, p.mutation_index, p.elite);
}
std::string describe(const nilm::SaParams& p) {
    return std::format("sa: chains {}, max_iter {}, threshold {}, patience {}, temperature {} (0 = auto), temp_min {}, cooling {} (0 = auto), step_frac {}",
                       p.chains, p.max_iter, p.threshold, p.patience, p.temperature, p.temp_min, p.cooling, p.step_frac);
}
std::string describe(const nilm::AcoParams& p) {
    return std::format("aco: archive {}, ants {}, max_iter {}, threshold {}, patience {}, q {}, xi {}", p.archive, p.ants, p.max_iter,
                       p.threshold, p.patience, p.q, p.xi);
}
std::string describe(const nilm::GdParams& p) {
    return std::format("gd: starts {}, max_iter {}, threshold {}, patience {}, step {}, fd_frac {}", p.starts, p.max_iter, p.threshold,
                       p.patience, p.step, p.fd_frac);
}
std::string describe(const nilm::NewtonParams& p) {
    return std::format("newton: starts {}, max_iter {}, threshold {}, patience {}, damping {}, fd_frac {}", p.starts, p.max_iter,
                       p.threshold, p.patience, p.damping, p.fd_frac);
}

double reconstruction_mae(const nilm::Dataset& d, std::span<const double> coefs) {
    double err = 0.0;
    for (std::size_t i = 0; i < d.size(); ++i) err += std::abs(d.aggregate[i] - nilm::reconstruct(coefs, d.sample(i)));
    return err / static_cast<double>(d.size());
}

struct Fit {
    std::vector<double> coefs;  // physical units
    std::size_t optimised = 0;  // samples with at least one machine on
    double mean_fitness = 0.0, mean_iterations = 0.0, mean_evaluations = 0.0;  // over the optimised samples
};

// One pass over the dataset: one optimisation per sample on the normalised
// aggregate, then the mean of each machine's coefficients over the samples in
// which it was on, converted back to physical units.
Fit fit(const nilm::Dataset& d, double scale, const Options& o, const Params& params, std::uint64_t seed) {
    const std::size_t machines = d.machines();
    const std::size_t dim = machines * nilm::kCoefs;
    const std::vector<double> lo(dim, -o.bound), hi(dim, o.bound);

    std::vector<nilm::Result> best(d.size());  // stays empty for samples with every machine off
    const auto n = static_cast<std::ptrdiff_t>(d.size());
#ifdef _OPENMP
#pragma omp parallel for schedule(dynamic)
#endif
    for (std::ptrdiff_t i = 0; i < n; ++i) {
        const auto idx = static_cast<std::size_t>(i);
        const nilm::Sample s{d.aggregate[idx] / scale, d.states[idx]};
        if (std::ranges::none_of(s.on, [](int on) { return on != 0; })) continue;
        std::uint64_t evaluations = 0;
        auto f = [&](std::span<const double> c) {
            ++evaluations;
            return nilm::objective(c, s, o.lambda);
        };
        best[idx] = std::visit([&](const auto& p) { return run(f, lo, hi, p, seed + idx); }, params);
        best[idx].evaluations = evaluations;
    }

    Fit r;
    std::vector<std::vector<double>> positions(d.size());
    for (std::size_t i = 0; i < d.size(); ++i) {
        if (best[i].position.empty()) continue;
        ++r.optimised;
        r.mean_fitness += best[i].fitness;
        r.mean_iterations += best[i].iterations;
        r.mean_evaluations += static_cast<double>(best[i].evaluations);
        positions[i] = std::move(best[i].position);
    }
    if (r.optimised) {
        r.mean_fitness /= static_cast<double>(r.optimised);
        r.mean_iterations /= static_cast<double>(r.optimised);
        r.mean_evaluations /= static_cast<double>(r.optimised);
    }
    r.coefs = nilm::unscale(nilm::average_on(positions, d.states, machines), scale);
    return r;
}

// One optimisation of the mean per-sample objective over all samples with at
// least one machine on; the result is the coefficient set itself.
Fit fit_joint(const nilm::Dataset& d, double scale, const Options& o, const Params& params, std::uint64_t seed) {
    const std::size_t dim = d.machines() * nilm::kCoefs;
    const std::vector<double> lo(dim, -o.bound), hi(dim, o.bound);
    std::vector<nilm::Sample> samples;
    for (std::size_t i = 0; i < d.size(); ++i)
        if (std::ranges::any_of(d.states[i], [](int on) { return on != 0; })) samples.push_back({d.aggregate[i] / scale, d.states[i]});

    Fit r{std::vector<double>(dim, 0.0), samples.size()};
    if (samples.empty()) return r;
    std::uint64_t evaluations = 0;
    auto f = [&](std::span<const double> c) {
        ++evaluations;
        double sum = 0.0;
        for (const auto& s : samples) sum += nilm::objective(c, s, o.lambda);
        return sum / static_cast<double>(samples.size());
    };
    const nilm::Result best = std::visit([&](const auto& p) { return run(f, lo, hi, p, seed); }, params);
    r.mean_fitness = best.fitness;
    r.mean_iterations = best.iterations;
    r.mean_evaluations = static_cast<double>(evaluations);
    r.coefs = nilm::unscale(best.position, scale);
    return r;
}

}  // namespace

int main(int argc, char** argv) try {
    const Options o = parse(argc, argv);
    const Params params = make_params(o);
    const nilm::Dataset d = nilm::load_dataset(o.aggregate, o.states);
    const double scale = nilm::scale_of(d.aggregate);
    int threads = 1;
#ifdef _OPENMP
    threads = omp_get_max_threads();
#endif
    std::cout << std::format("{} samples, {} machines, aggregate scale {}, bound {}, lambda {}, {} fit, {} thread(s), seed {}\n{}\n", d.size(),
                             d.machines(), scale, o.bound, o.lambda, o.joint ? "joint" : "per-sample", o.joint ? 1 : threads, o.seed,
                             std::visit([](const auto& p) { return describe(p); }, params));
    for (std::size_t j = 0; j < d.machines(); ++j)
        if (std::ranges::none_of(d.states, [j](const auto& on) { return on[j] != 0; }))
            std::cerr << std::format("warning: machine {} is never on, its coefficients stay 0\n", j);

    double best_mae = std::numeric_limits<double>::infinity();
    if (std::filesystem::exists(o.out)) {
        const auto existing = nilm::read_coefs(o.out);
        if (existing.size() != d.machines() * nilm::kCoefs)
            throw std::runtime_error(std::format("{} holds {} machines, states hold {}", o.out.string(),
                                                 existing.size() / nilm::kCoefs, d.machines()));
        best_mae = reconstruction_mae(d, existing);
        std::cout << std::format("existing {}: MAE {:.6g}\n", o.out.string(), best_mae);
    }
    for (int c = 0; c < o.cycles; ++c) {
        const auto t0 = std::chrono::steady_clock::now();
        const auto cycle_seed = o.seed + static_cast<std::uint64_t>(c) * d.size();
        const Fit r = o.joint ? fit_joint(d, scale, o, params, cycle_seed) : fit(d, scale, o, params, cycle_seed);
        const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        const double mae = reconstruction_mae(d, r.coefs);
        const bool better = mae < best_mae;
        std::cout << std::format("cycle {}: MAE {:.6g}  samples used {}  {}fitness {:.3g}  {}iterations {:.1f}  {}evaluations {:.0f}  {:.1f}s{}\n",
                                 c, mae, r.optimised, o.joint ? "" : "mean ", r.mean_fitness, o.joint ? "" : "mean ", r.mean_iterations,
                                 o.joint ? "" : "mean ", r.mean_evaluations, seconds, better ? "  -> saved" : "");
        if (better) {
            nilm::write_coefs(o.out, r.coefs);
            best_mae = mae;
        }
    }
    return 0;
} catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
}
