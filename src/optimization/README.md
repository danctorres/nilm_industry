# EMUPF estimation

Models each machine's active power as a cubic polynomial of the aggregate active
power, switched by the machine's on/off state. Every training sample with at
least one machine on is one optimisation problem over all coefficients; the
coefficients of the machines that were on are averaged over all samples.
`estimate` repeats this for a number of random restarts and keeps the
coefficient set with the lowest reconstruction error, also against an existing
coefficient file.

Fitting runs on the aggregate divided by its largest value, so `--bound`,
`--threshold` and the reported fitness are unit-free and the same for HIPE (kW)
and IMDELD (W). The coefficient file is written in physical units, so
`validate` and the MATLAB scripts are unaffected. All algorithms confine the
coefficients to `[-bound, bound]`.

The point of the module is to compare optimisation algorithms on this problem.
All six share one interface (`optimizer.h`) and are selected with `--algorithm`:

| flag     | header       | method                                                             |
|----------|--------------|--------------------------------------------------------------------|
| `pso`    | `pso.h`      | particle swarm, linearly decreasing inertia                        |
| `ga`     | `ga.h`       | real-coded GA: tournament, double Pareto crossover, power mutation |
| `sa`     | `sa.h`       | simulated annealing, independent chains, geometric cooling         |
| `aco`    | `aco.h`      | ACOR, ant colony for continuous domains                            |
| `gd`     | `gradient.h` | gradient descent with Armijo backtracking, multi-start             |
| `newton` | `gradient.h` | damped Newton (Levenberg-Marquardt), multi-start                   |

The gradient methods use central finite differences, so every algorithm sees the
objective as a black box. Algorithm-specific constants are the defaults of each
`Params` struct in its header; the CLI exposes only the shared knobs, and every
run prints the full parameter set it used.

Other files: `model.h` (polynomial, objective, metrics), `io.h` (CSV, dataset,
results), `estimate.cpp`, `validate.cpp`, `tests.cpp`.

## Build and test

```sh
cmake -S src/optimization -B build && cmake --build build -j && ctest --test-dir build
```

## Run

```sh
# IMDELD, 6 machines. OMP_NUM_THREADS controls parallelism.
OMP_NUM_THREADS=8 build/estimate \
    data/processed/IMDELD/data_6_equipment/aggregate_training.csv \
    data/processed/IMDELD/data_6_equipment/on_off_training.csv \
    results/optimization/IMDELD/estimated_coef_6.csv

build/validate \
    data/processed/IMDELD/data_6_equipment/aggregate_validation.csv \
    data/processed/IMDELD/data_6_equipment/on_off_validation.csv \
    data/processed/IMDELD/data_6_equipment/equipment_validation.csv \
    results/optimization/IMDELD/estimated_coef_6.csv \
    results/optimization/IMDELD/estimated_active_power_6.csv
```

HIPE uses the same commands with `data/processed/HIPE/1_week/{aggregate,state,equipment}_*/..._N.csv`.

`estimate` options: `--algorithm pso` (default), `--joint` (one optimisation of
the mean per-sample objective over all samples, no averaging), `--cycles 5`, `--particles N`
(population for pso and ga, archive for aco, chains for sa, starts for gd and
newton; default is each algorithm's own), `--iters 200`, `--threshold 1e-5`
(on the normalised objective), `--bound 1` (coefficient box, normalised units),
`--lambda 1` (negative-power penalty weight), `--seed N` (reproducible runs,
independent of the thread count). Each cycle prints the reconstruction MAE in
physical units, how many samples were optimised, the mean final fitness, mean
iterations and mean objective evaluations of the per-sample optimisations, and
the wall time. Compare algorithms on evaluations, not iterations: one PSO
iteration costs `particles` evaluations, one ACO iteration costs `ants`.

```sh
for a in pso ga sa aco gd newton; do
  build/estimate agg.csv states.csv results/coef_$a.csv --algorithm $a --seed 1
done
```

CSV layout: aggregate file is `timestamp, active power[, ...]`; state and
equipment files are `timestamp` followed by one column per machine; the
coefficient file has one row of four coefficients per machine.

## Limitation of the method

Each per-sample problem is one residual in `4 x machines` unknowns, so its
exact minimisers form a whole affine set and every algorithm returns some point
of it; the per-machine average of such points is not a least-squares model. The
per-sample problem is also convex, which is why Newton solves it in one step.
The algorithm comparison therefore says more about convergence speed on an
under-determined quadratic than about model quality. On the synthetic data the
averaged coefficients still reconstruct the aggregate about six times better
than predicting zero. `estimate --joint` fits one objective over all samples
instead, which is well-posed and gives the stronger baseline to compare against.
