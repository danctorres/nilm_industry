# Polynomial model

> **In short:** each machine's power is a **cubic polynomial of the total**, fitted by **six optimisers** so they can be compared. For the best fit, use **`estimate --joint`**.

## How it works

* **Model:** a machine's active power is a cubic polynomial of the total active power while it is on, 0 while off.
* **Fit:** each training sample with at least one machine on is one optimisation problem over all coefficients. Each machine's coefficients are then averaged over the samples where it was on.
* **Restarts:** `estimate` repeats this for `--cycles` random restarts and keeps the coefficient set with the lowest reconstruction error, also against an existing coefficient file.
* **No units:** the fit runs on the total divided by its largest value, so `--bound`, `--threshold` and the reported fitness are the same for HIPE (kW) and IMDELD (W). The coefficient file is in physical units, so `validate` is unaffected.
* **Box:** all algorithms keep the coefficients in `[-bound, bound]`.

## The six algorithms

All share one interface ([`optimizer.h`](optimizer.h)), picked with `--algorithm`:

| flag | header | method |
|---|---|---|
| `pso` | [`pso.h`](pso.h) | particle swarm; inertia (the share of its velocity a particle keeps) falls linearly |
| `ga` | [`ga.h`](ga.h) | real-coded GA: tournament (best of a few random picks), double Pareto crossover, power mutation |
| `sa` | [`sa.h`](sa.h) | simulated annealing, independent chains, geometric cooling |
| `aco` | [`aco.h`](aco.h) | ACOR, ant colony for continuous domains |
| `gd` | [`gradient.h`](gradient.h) | gradient descent, Armijo backtracking (halve the step until the cost drops enough), multi-start |
| `newton` | [`gradient.h`](gradient.h) | damped Newton (Levenberg-Marquardt: damping keeps the step defined), multi-start |

* **Black box:** the gradient methods use central finite differences, so every algorithm sees only the objective's values.
* **Settings:** algorithm-specific constants are the defaults of each `Params` struct in its header. The CLI sets only the shared knobs. **Every run prints the full parameter set it used.**
* **Other files:** [`model.h`](model.h) (polynomial, objective), [`io.h`](io.h) (CSV, dataset, results), `estimate.cpp`, `validate.cpp`, `tests.cpp`.

## Build and test

```sh
cmake -S src/polynomial -B build && cmake --build build -j && ctest --test-dir build
```

The first configure downloads [doctest](https://github.com/doctest/doctest) for `tests.cpp`.

## Run

IMDELD, 6 machines. `OMP_NUM_THREADS` controls parallelism.

```sh
OMP_NUM_THREADS=8 build/estimate \
    data/processed/IMDELD/6/aggregate_training.csv \
    data/processed/IMDELD/6/states_training.csv \
    results/polynomial/IMDELD/coef_6.csv
```

```sh
build/validate \
    data/processed/IMDELD/6/aggregate_validation.csv \
    data/processed/IMDELD/6/states_validation.csv \
    results/polynomial/IMDELD/coef_6.csv \
    results/polynomial/IMDELD/6.csv
```

* **HIPE:** same commands, with `HIPE/<N>` in place of `IMDELD/6`.
* **Keep the estimates at `results/polynomial/<DATASET>/<N>.csv`** so [`validation.py`](../validation/validation.py) finds them.

### `estimate` options

| option | default | meaning |
|---|---|---|
| `--algorithm` | `pso` | `pso`, `ga`, `sa`, `aco`, `gd` or `newton` |
| `--joint` | off | one optimisation of the mean per-sample objective over all samples, no averaging |
| `--cycles` | 5 | random restarts |
| `--particles N` | each algorithm's own | population (pso, ga), archive (aco), chains (sa), starts (gd, newton) |
| `--iters` | 200 | max iterations |
| `--threshold` | 1e-5 | on the normalised objective |
| `--bound` | 1 | coefficient box, normalised units |
| `--lambda` | 1 | negative-power penalty weight: each negative estimate p adds `lambda * (2.5 p)^2` |
| `--seed N` | random | reproducible runs, independent of the thread count |

**Each cycle prints:**
* the reconstruction MAE, in physical units;
* how many samples were optimised;
* the mean final fitness, iterations and objective evaluations of the per-sample optimisations;
* the wall time.

**Compare algorithms on evaluations, not iterations:** one PSO iteration costs `particles` evaluations, one ACO iteration costs `ants`.

```sh
for a in pso ga sa aco gd newton; do
  build/estimate agg.csv states.csv results/coef_$a.csv --algorithm $a --seed 1
done
```

### CSV layout

* **Aggregate:** `timestamp, active power[, ...]`.
* **States and equipment:** `timestamp`, then one column per machine.
* **Coefficients:** one row of four per machine.

## Limitation of the method

> **In short:** the default per-sample fit is badly underdetermined. Compare against `--joint`.

* **Each per-sample problem is one residual in `4 x machines` unknowns.** Its exact minimisers form a whole affine set, and every algorithm returns some point of it.
* **The per-machine average of such points is not a least-squares model.**
* **Each per-sample cost is quadratic in the coefficients** while no negative-power penalty is active, so damped Newton gets there in about one step.
* **So the algorithm comparison** says more about convergence speed on an under-determined quadratic than about model quality.
* **`estimate --joint`** fits one objective over all samples instead: well-posed, and the stronger baseline.
