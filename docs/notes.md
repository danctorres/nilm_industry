# Notes

> **What's here:** everything behind the [README](../README.md). Each section stands on its own, so jump straight to the one you need.

| Section | Read it to... |
|---|---|
| [Words](#words) | learn the terms used below |
| [Results per group](#results-per-group) | see every number |
| [Get the data](#get-the-data) | download HIPE or IMDELD |
| [Prepare the data](#prepare-the-data) | know what the files contain |
| [Run the methods](#run-the-methods) | see every option |
| [How the settings were chosen](#how-the-settings-were-chosen) | know why the defaults are what they are |
| [Why the states must be given](#why-the-states-must-be-given) | use this on a real plant |
| [Why IMDELD cannot be split](#why-imdeld-cannot-be-split) | make sense of the IMDELD numbers |

## Words

* **Total**: all the machines' power together. Called `aggregate` in the files.
* **State**: on or off, for each machine at each second.
* **Group**: N machines whose power is added into one total. HIPE has groups of 2 to 10.
* **Error (MAE)**: the average gap between estimated and metered power, in W.
* **NDE**: squared error ÷ squared metered power. 0 is perfect; 1 is as bad as guessing 0 W.
* **Baselines**: three simple guesses every method should beat:
  * guess 0 W;
  * split the total equally among the running machines;
  * split it in proportion to each machine's average power.

## Results per group

> **In short:** Gaussian allocation wins on every group. Nothing else beats the proportional split on average.

**Setup:** HIPE · trained on November 2017 · scored on December · settings chosen on October · error in W · seeds: preprocessing 1, neural network 0, polynomial model 1.

| Method | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Gaussian allocation | 4.0 | 3.3 | 2.1 | 9.2 | 7.2 | 6.3 | 6.0 | 5.9 | 13.7 | 6.4 |
| Gaussian allocation, 1 level per machine | 3.6 | 3.2 | 2.8 | 9.7 | 8.4 | 7.6 | 6.8 | 6.8 | 15.1 | 7.1 |
| Neural network, total only as input | 7.8 | 10.9 | 11.8 | 21.2 | 16.6 | 18.4 | 18.2 | 18.2 | 44.9 | 18.7 |
| Neural network, total and states as input | 15.2 | 21.0 | 20.7 | 22.6 | 14.8 | 21.7 | 14.1 | 18.8 | 31.9 | 20.1 |
| Polynomial model, fitted sample by sample | 72.9 | 60.2 | 48.1 | 58.0 | 47.8 | 43.7 | 38.9 | 34.9 | 47.7 | 50.2 |
| Polynomial model, fitted to all samples at once | 10.3 | 11.3 | 11.4 | 21.1 | 19.6 | 21.2 | 18.9 | 22.9 | 57.4 | 21.6 |
| Hart-inspired | 72.7 | 54.9 | 46.5 | 47.7 | 40.2 | 46.4 | 43.2 | 41.2 | 66.5 | 51.0 |
| Baseline: guess 0 W | 73.2 | 55.3 | 47.4 | 48.4 | 40.7 | 46.6 | 43.4 | 41.3 | 66.7 | 51.4 |
| Baseline: equal split | 20.6 | 24.8 | 27.5 | 30.9 | 25.9 | 30.4 | 27.3 | 26.1 | 42.1 | 28.4 |
| Baseline: proportional split | 11.6 | 11.7 | 14.9 | 18.7 | 14.2 | 20.4 | 17.3 | 15.7 | 33.3 | 17.5 |

* **Gaussian allocation** is best on every group. With 1 level per machine it is slightly better on groups 2 and 3.
* **Beating the proportional split:** the polynomial model (all at once) on groups 2–4, the neural network (total only) on 2–4 and 7, and with states on 8 and 10. None of them on average.
* **Group 10 is the hardest.** Its extra machine, the ChipPress, runs only in November and December, so October never shows its big loads.

### Older: the one-week release

> **In short:** the same picture on HIPE. On IMDELD, nothing reliably beats guessing 0 W.

**Setup:**
* HIPE's one-week release (23 to 30 Oct 2017), with random hours held out for testing.
* Older method versions: 1 level per machine in Gaussian allocation, and the neural network's original training.
* Error in kW, mean ± spread over 3 splits (preprocessing seeds 1, 2 and 3).

| Method | HIPE, 9 | IMDELD, 6 | IMDELD, 8 |
|---|---|---|---|
| Gaussian allocation | 0.021 ± 0.014 | 37.6 ± 1.5 | 31.7 ± 3.2 |
| Neural network, total only | 0.039 ± 0.019 | 20.9 ± 2.9 | 22.8 ± 0.8 |
| Neural network, total and states | 0.055 ± 0.015 | 26.6 ± 1.9 | 24.3 ± 3.4 |
| Polynomial model, sample by sample | 0.047 ± 0.014 | 22.9 ± 0.8 | 18.6 ± 0.4 |
| Polynomial model, all samples at once | 0.043 ± 0.022 | 19.4 ± 1.9 | 17.3 ± 3.5 |
| Hart-inspired (estimates only 7–17% of the on-samples) | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: guess 0 W | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: equal split | 0.039 ± 0.016 | 24.1 ± 1.0 | 19.0 ± 0.2 |
| Baseline: proportional split | 0.036 ± 0.012 | 37.4 ± 2.2 | 32.5 ± 3.5 |

* **The spread** mostly reflects which hours or days were held out.
* **HIPE, 24 cases** (groups 2–9 × 3 splits). Cases where each method beats the best baseline:
  * Gaussian allocation: all 24;
  * neural network (total only): 5;
  * neural network (with states) and polynomial model (all at once): 3;
  * polynomial model (sample by sample): none.
* **IMDELD:** the polynomial model (all at once) beats the best baseline in 4 of 6 cases, but by less than the spread, and the best method changes from split to split. [Why.](#why-imdeld-cannot-be-split)

## Get the data

> **In short:** HIPE downloads with one command. IMDELD needs a free account and three manual downloads.

Neither dataset is included, and each keeps its own terms. Everything goes in `data/raw`.

### HIPE

From Bischof et al., [KIT](https://www.energystatusdata.kit.edu/hipe.php).

```sh
uv run src/preprocessing/fetch_hipe.py
```

* Downloads the three-month release (1 Oct 2017 to 1 Jan 2018) from [Zenodo](https://doi.org/10.5281/zenodo.14054902): 1.33 GB, 30.6 GB unpacked, checksum verified.
* Puts the 10 machine files in `data/raw/HIPE/Equipment`, and the main meter (`MainTerminal`) in `data/raw/HIPE`.

### IMDELD

From Martins et al., [IEEE DataPort](https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation). Needs a free IEEE account. From the dataset's file list:

1. `Appliances.zip`: unpack its 8 machine files into `data/raw/IMDELD/Equipment`.
2. "Pelletizer SubCircuit", the total meter: save it as `data/raw/IMDELD/pelletizer-subcircuit.csv`.
3. "Milling Machines SubCircuit", only needed for the 8-machine group: save it as `data/raw/IMDELD/millingmachine-subcircuit.csv`.

## Prepare the data

> **In short:** two commands turn the raw files into training and test sets for each group.

```sh
uv run src/preprocessing/hipe.py     # about 30 min, 8 GB of output
uv run src/preprocessing/imdeld.py   # add --equipment 1,2,3,4,5,6,7,8 for the 8-machine group
```

### Output files

In `data/processed/<DATASET>/<N>/`, where N is the number of machines in the group:

| File | Columns |
|---|---|
| `aggregate*.csv` | `timestamp`, then the total in `active_power` |
| `states*.csv` | `timestamp`, then one 0/1 column per machine |
| `equipment*.csv` | `timestamp`, then each machine's metered power (for scoring only) |

* **Three versions of each:** `_training` (training rows), `_validation` (test rows), and no suffix (the whole recording).
* **Units:** HIPE in kW, IMDELD in W. Both have one row per second.

### Which machines are in each group

* **HIPE, N = 2 to 9:** machines 2 to N + 1, in alphabetical file order.
* **HIPE, N = 10:** adds machine 1, the ChipPress. It comes last because it was always off in the one-week release.
* **IMDELD, N = 6:** machines 1, 2, 3, 4, 7 and 8. **N = 8:** all of them.

### How the total is made

* **HIPE: the sum of the group's machine meters, not the main meter.**
  * The 10 machines are only 4% of the main meter's energy (0.58 kW against 14.0 kW on average).
  * The rest is other plant load, about 8 kW at night and 20 kW at midday.
  * The methods would wrongly give that load to the running machines.
* **IMDELD: a real meter.** 2–3% of it comes from equipment without its own meter, which the methods have to give to some machine.

### On or off

* **HIPE:** on when the power is above 0, after resampling to one value per second and rounding to 0.1 W.
* **IMDELD:** on when the power is above 5 W.

### Cleaning

* **IMDELD** is smoothed with a 25-minute moving average, restarted after each gap between days. HIPE is not smoothed.
* **HIPE timestamps are in UTC**, so there is no jump at the end of summer time (29 Oct 2017).
* **HIPE gaps:** wherever any machine has a gap of more than 300 s, those rows are dropped from every machine. This happens twice: 8.5 min on 10 Nov, and 21 h in the VacuumOven on 14–15 Dec.

### Training and test rows

* **HIPE** is split by month (UTC): October for tuning, November for training, December for the reported scores.
* **IMDELD** holds out 30% of its days for testing, picked at random with `--seed` (1 by default).
* **Test rows:** every row of the test month or days.
* **Training rows:** about 3,000 rows sampled from the rest, up to 490 from each of 6 power ranges, so the peaks are included. For HIPE, `--seed` only changes which rows are drawn.
* **No overlap:** rows near a cut between parts are dropped (300 s for HIPE, 750 s for IMDELD), so no reading is in two parts.

### The tuning copy

`hipe.py` also writes `tuning/data`: the same sets, but tested on October. **Choose settings on it, and report December only for what was chosen on October.**

* Methods: add `--data-root tuning/data --results-root tuning/results/<method>`.
* `validation.py`: add `--data-root tuning/data --results-root tuning/results`.
* Polynomial model: use the paths under `tuning/data/HIPE/<N>`.

## Run the methods

> **In short:** each method trains on the training rows and writes estimates for the test rows to `results/<method>/<DATASET>/<N>.csv`. Then `validation.py` scores them.

### Gaussian allocation

```sh
uv run src/allocation/allocation.py --dataset {hipe,imdeld} --machines N [--components {K,auto}]
```

* **`K`:** power levels per machine (idle, heating, ...). Default 3.
* **`auto`:** each machine gets its own number of levels, up to 5. Levels are added one at a time while they improve the fit to the training rows by more than BIC's penalty.
* **Slow** when many machines are on at once, since it tries every combination of levels.
* **Assumes** the machines switch on and off independently, and warns when two don't.

### Neural network

```sh
uv run src/neural_network/main.py --dataset {hipe,imdeld} --mode {plain,state} --machines N [--runs R] [--epochs E] [--seed S]
```

* **`plain`:** the input is the total only. **`state`:** the total and the states.
* **`--runs`:** trains R networks (5 by default) from different random starts, and averages them.
* **Output** goes to `results/neural_network/<mode>/...`.

### Polynomial model (C++)

Needs CMake 3.20 or later and a C++20 compiler (GCC 13 tested). OpenMP is optional.

```sh
cmake -S src/polynomial -B build && cmake --build build -j && ctest --test-dir build
```

Then run `estimate` and `validate`, as described in [its README](../src/polynomial/README.md).

### Hart-inspired

```sh
uv run src/hart_inspired/hart_inspired.py --dataset hipe --machines 9
```

* **No training.** It estimates the whole recording and is scored on the test rows.
* **Partial:** it only estimates a machine where it can match the machine's switch-off with a step in the total.

### Scoring

```sh
uv run src/validation/validation.py [--plots DIR]
```

* Compares every results file with the metered power.
* Also scores the 3 [baselines](#words).
* The last lines give one line per method: error and NDE.

### Self-checks

Every Python folder has one, e.g. `uv run src/validation/test_validation.py`. The first `uv run` builds the environment from `uv.lock`.

## How the settings were chosen

> **In short:** everything was chosen on October. The numbers are means over HIPE groups 2 to 10.

### Gaussian allocation: 3 levels per machine

* **Against 1 level:** error −7 to −32% on groups 4 to 10 in October, and −5 to −24% in December.
* **Groups 2 and 3:** 1 level stays slightly better.
* **`--components auto`:** barely better in October (5.98 W against 6.06 W), worse in December (6.67 W against 6.40 W). Not the default.

### Neural network

| Setting | Now | Before |
|---|---|---|
| Training | Adam, batches of 64 rows, learning rate 0.01 → 0 over 2000 epochs | plain gradient descent, one row at a time |
| Hidden units | 64 | N + 1 |
| Weight decay | 0.1 (total only), 0.01 (with states) | none |
| Runs | average of 5 | the one with the lowest training loss |

Change against before:

| Input | October error | December error | October NDE | December NDE |
|---|---|---|---|---|
| Total only | −19% | −8% | −13% | −21% |
| Total and states | −60% | −29% | −76% | −32% |

* **Why weight decay:** with the total as its only input, the network over-fits the ~3,000 training rows. Without decay, its NDE got worse instead of better.
* **Why average the runs:** with the states as input, many different splits of the total fit the training data equally well, so each run picks its own. Averaging evens this out.
  * Before averaging (one-week tests), results moved with the seed. HIPE group 9: 53 ± 5 W with the states, 36 ± 1 W with the total only. IMDELD group 6, total only: 25 ± 6 kW, against 20.5 kW for guessing 0.
  * **So compare the neural network over several seeds.**

### Polynomial model: fit all samples at once

* **Sample by sample** (the dissertation's version) solves one equation with 4 × N unknowns at each sample, then averages the answers. That is badly underdetermined: see [its README](../src/polynomial/README.md#limitation-of-the-method).
* **`estimate --joint`** fits all samples at once. **Compare this one.**

### Tried and dropped

* **Tuning the polynomial model's optimisers:** the defaults did as well.
* **Smoothing Gaussian allocation's estimates over time:** only 6% better, not worth the code.
* **Tracking each machine's power level over time:** worse. Neighbouring seconds don't reveal a machine's level any better than the second itself; they just make wrong guesses more confident.

## Why the states must be given

> **In short:** the methods need accurate, on-time on/off signals. Guessing them from the total doesn't work.

### Test it yourself

```sh
uv run src/validation/corrupt_states.py --dataset hipe --machines N (--lag S | --flip P) --out DIR
```

* **`--lag S`:** every state reported S seconds late.
* **`--flip P`:** each state flipped with probability P.
* Then run the methods and the scoring with `--data-root DIR`.

### What happens

Gaussian allocation on the one-week release, mean over groups 2 to 9:

| States | Error (W) |
|---|---|
| exact | 10.5 |
| 10 s late | 11.2 |
| 60 s late | 27.5 |
| 1% flipped | 20.9 |
| *Proportional split, exact states* | *31.2* |

With states 60 s late, it still beats the best baseline given the same late states on 4 of the 8 groups.

### Why not work out the states from the total?

In HIPE group 9:
* The total jumps by more than 50 W within 240 s **2,213 times**.
* Only **322** of those come within 240 s of a machine switching on or off.
* The rest are machines changing their load while on.
* One 8 W machine, which switches 2,215 times, is left out of this count.

## Why IMDELD cannot be split

> **In short:** its machines switch on and off together, so their power can't be told apart.

* **State correlation** between its machines: 0.93 to 1.00.
* **In 96% of the samples,** every machine is on or every machine is off.
* **Grouping** the machines that switch together leaves just one group.
* **So:** compare any IMDELD result with the baselines before reading anything into it.
