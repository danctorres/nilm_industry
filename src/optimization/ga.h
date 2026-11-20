#pragma once
// Real-coded genetic algorithm after Thakur (2014): tournament selection,
// double Pareto crossover, power mutation (Deep & Thakur 2007) and elitism.
#include "optimizer.h"

namespace nilm {

struct GaParams {
    int population = 100;
    int max_iter = 200;
    double threshold = 1e-5;
    int patience = 10;
    int tournament = 2;           // candidates per tournament
    double alpha = 2.0;           // double Pareto shape: smaller means heavier tails
    double beta = 0.5;            // double Pareto scale
    double p_mutation = 0.1;      // per-variable mutation probability
    double mutation_index = 0.5;  // power mutation index: smaller means smaller moves
    int elite = 1;                // best individuals copied unchanged
};

template <Objective F>
[[nodiscard]] Result ga(F&& f, std::span<const double> lo, std::span<const double> hi, const GaParams& p, std::uint64_t seed) {
    const std::size_t dim = lo.size();
    std::mt19937_64 rng(seed);
    std::uniform_int_distribution<std::size_t> pick(0, static_cast<std::size_t>(p.population) - 1);

    struct Ind {
        std::vector<double> x;
        double fit;
    };
    const auto by_fit = [](const Ind& a, const Ind& b) { return a.fit < b.fit; };
    std::vector<Ind> pop(static_cast<std::size_t>(p.population));
    for (auto& ind : pop) {
        ind.x = random_point(rng, lo, hi);
        ind.fit = f(std::span<const double>(ind.x));
    }
    std::sort(pop.begin(), pop.end(), by_fit);
    Result best;
    best.offer(pop.front().x, pop.front().fit);

    const auto select = [&]() -> const Ind& {
        const Ind* winner = &pop[pick(rng)];
        for (int t = 1; t < p.tournament; ++t)
            if (const Ind* c = &pop[pick(rng)]; c->fit < winner->fit) winner = c;
        return *winner;
    };
    const auto pareto = [&]() {  // sample of the double Pareto distribution, median 0, kept finite
        const double u = std::clamp(unit01(rng), 1e-12, 1.0 - 1e-12);
        return u < 0.5 ? p.beta * (1 - std::pow(2 * u, -1 / p.alpha)) : p.beta * (std::pow(2 * (1 - u), -1 / p.alpha) - 1);
    };
    const auto mutate = [&](std::vector<double>& x) {  // power mutation, keeps x inside [lo, hi]
        for (std::size_t k = 0; k < dim; ++k) {
            if (unit01(rng) >= p.p_mutation || x[k] <= lo[k] || x[k] >= hi[k]) continue;  // boundary points stay put
            const double s = std::pow(unit01(rng), 1 / p.mutation_index);
            const double t = (x[k] - lo[k]) / (hi[k] - x[k]);
            x[k] = t < unit01(rng) ? x[k] - s * (x[k] - lo[k]) : x[k] + s * (hi[k] - x[k]);
        }
    };

    Stopper stop{p.threshold, p.patience};
    for (int it = 0; it < p.max_iter; ++it) {
        const auto elite = static_cast<std::ptrdiff_t>(std::clamp(p.elite, 0, p.population));
        std::vector<Ind> next(pop.begin(), pop.begin() + elite);
        while (next.size() < pop.size()) {
            const Ind& a = select();
            const Ind& b = select();
            std::vector<double> c1(dim), c2(dim);
            for (std::size_t k = 0; k < dim; ++k) {
                const double mid = (a.x[k] + b.x[k]) / 2, half = std::abs(a.x[k] - b.x[k]) / 2, bk = pareto();
                c1[k] = mid + bk * half;
                c2[k] = mid - bk * half;
            }
            for (auto* c : {&c1, &c2}) {
                if (next.size() == pop.size()) break;
                clamp_to(*c, lo, hi);
                mutate(*c);
                const double fit = f(std::span<const double>(*c));
                next.push_back({std::move(*c), fit});
            }
        }
        pop = std::move(next);
        std::sort(pop.begin(), pop.end(), by_fit);
        best.offer(pop.front().x, pop.front().fit);
        best.iterations = it + 1;
        if (stop.done(best.fitness)) break;
    }
    return best;
}

}  // namespace nilm
