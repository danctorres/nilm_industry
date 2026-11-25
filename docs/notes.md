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
* **Error (MAE)**: the average gap between estimated and metered power, in W, over every test second. That includes the seconds a machine is off, where every method is exactly right (it gives 0 W), and the machines are off most of the time.
* **Error while running**: the same, over only the seconds a machine draws power. Much larger.
* **NDE**: squared error ÷ squared metered power. 0 is perfect; 1 is as bad as guessing 0 W.
* **Baselines**: three simple guesses every method should beat:
  * guess 0 W;
  * split the total equally among the running machines;
  * split it in proportion to each machine's average power, as estimated from the training totals. Where only machines estimated at 0 W are on, they split it equally.

## Results per group

> **In short:** Gaussian allocation wins on every group. The neural network is second, the only other method to beat the proportional split on average.

**Setup:** HIPE · trained on November 2017 · scored on December · settings chosen on October · error in W · seeds: preprocessing 1, neural network 0.

| Method | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Mean | Mean while running |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Gaussian allocation | 2.7 | 2.8 | 2.2 | 8.7 | 7.4 | 6.5 | 6.0 | 5.9 | 13.4 | 6.2 | 101 |
| Gaussian allocation, 1 level per machine | 3.6 | 3.7 | 2.9 | 9.7 | 8.2 | 7.5 | 6.7 | 6.5 | 14.5 | 7.0 | 115 |
| Neural network, total only as input | 5.1 | 6.7 | 5.1 | 13.8 | 11.2 | 12.3 | 11.6 | 12.4 | 24.2 | 11.4 | 185 |
| Neural network, total and states as input | 12.8 | 12.4 | 19.7 | 17.7 | 12.5 | 13.3 | 11.8 | 10.0 | 23.2 | 14.8 | 234 |
| Hart-inspired | 72.6 | 54.5 | 45.9 | 46.5 | 39.1 | 44.4 | 41.3 | 39.4 | 62.4 | 49.6 | 789 |
| Baseline: guess 0 W | 73.2 | 55.3 | 47.4 | 48.4 | 40.7 | 46.6 | 43.4 | 41.3 | 66.7 | 51.4 | 820 |
| Baseline: equal split | 20.6 | 24.8 | 27.5 | 30.9 | 25.9 | 30.4 | 27.3 | 26.1 | 42.1 | 28.4 | 454 |
| Baseline: proportional split | 8.3 | 9.5 | 14.1 | 18.3 | 15.8 | 19.6 | 18.2 | 17.8 | 30.5 | 16.9 | 273 |

* **Gaussian allocation** is best on every group, and 3 levels per machine beat 1 on every group.
* **Beating the proportional split:** the neural network (total only) on every group and on average. With states, on groups 5 to 10 and on average.
* **Hart-inspired** estimates 97–100% of the on-samples, yet is barely better than guessing 0 W.
* **Mean while running:** the mean over groups of the error over only the seconds a machine draws power. See [Words](#words).
* **Group 10 is the hardest.** Its extra machine, the ChipPress, runs only in November and December, so October never shows its big loads.

### IMDELD

> **In short:** nothing does much better than a simple guess. Gaussian allocation does much worse.

**Setup:** IMDELD · 30% of its days held out for testing, picked at random · 3 splits (preprocessing seeds 1, 2 and 3) · error in kW, mean over the splits (lowest–highest).

| Method | 6 machines | 8 machines |
|---|---|---|
| Gaussian allocation | 33.8 (31.6–35.5) | 29.0 (26.9–31.4) |
| Neural network, total only as input | 19.9 (19.4–20.4) | 20.1 (15.7–22.6) |
| Neural network, total and states as input | 21.7 (21.0–22.7) | 17.0 (16.2–18.3) |
| Hart-inspired | 20.1 (19.4–20.8) | 20.4 (20.0–20.8) |
| Baseline: guess 0 W | 20.1 (19.4–20.8) | 20.4 (20.0–20.9) |
| Baseline: equal split | 24.3 (23.5–25.1) | 19.0 (18.8–19.3) |
| Baseline: proportional split | 38.9 (37.4–40.3) | 32.4 (31.6–33.9) |

* **Against the best baseline** (guess 0 W on 6 machines, the equal split on 8), split by split:
  * the network with states, on 8 machines, wins all 3: by 3%, 15% and 14%;
  * the network with the total only, on 6 machines, wins all 3, by 2% or less;
* **Gaussian allocation** is 30–70% worse than guessing 0 W, and the proportional split worse still. Both learn each machine's power from the total, which can't work when the machines switch together. [Why.](#why-imdeld-cannot-be-split)
* **One split can mislead:** the network with the total only scores 15.7 kW on 8 machines with split 1, and 22–23 kW with the other two.
* **Hart-inspired** gives an estimate for 45–84% of the on-samples, yet is no better than guessing 0 W.

### Older: the one-week release

> **In short:** the same picture on HIPE. On IMDELD, nothing reliably beats guessing 0 W.

**Setup:**
* HIPE's one-week release (23 to 30 Oct 2017), with random hours held out for testing.
* Older method versions: 1 level per machine in Gaussian allocation, and the neural network's original training. Also from before the network's and Gaussian allocation's estimates were scaled to add up to the total, Hart-inspired's looser switch-off check, and the proportional split's fix for machines estimated at 0 W.
* Error in kW, mean ± spread over 3 splits (preprocessing seeds 1, 2 and 3).

| Method | HIPE, 9 | IMDELD, 6 | IMDELD, 8 |
|---|---|---|---|
| Gaussian allocation | 0.021 ± 0.014 | 37.6 ± 1.5 | 31.7 ± 3.2 |
| Neural network, total only | 0.039 ± 0.019 | 20.9 ± 2.9 | 22.8 ± 0.8 |
| Neural network, total and states | 0.055 ± 0.015 | 26.6 ± 1.9 | 24.3 ± 3.4 |
| Hart-inspired (estimates only 7–17% of the on-samples) | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: guess 0 W | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: equal split | 0.039 ± 0.016 | 24.1 ± 1.0 | 19.0 ± 0.2 |
| Baseline: proportional split | 0.036 ± 0.012 | 37.4 ± 2.2 | 32.5 ± 3.5 |

* **The spread** mostly reflects which hours or days were held out.
* **HIPE, 24 cases** (groups 2–9 × 3 splits). Cases where each method beats the best baseline:
  * Gaussian allocation: all 24;
  * neural network (total only): 5;
  * neural network (with states): 3.

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
* **Training rows:** 19,600 drawn at random from the rest, for every group. For HIPE, `--seed` only changes which rows are drawn.
* **No overlap:** rows near a cut between parts are dropped (300 s for HIPE, 750 s for IMDELD), so no reading is in two parts.

### The tuning copy

`hipe.py` also writes `tuning/data`: the same sets, but tested on October. **Choose settings on it, and report December only for what was chosen on October.**

* Methods: add `--data-root tuning/data --results-root tuning/results/<method>`.
* `validation.py`: add `--data-root tuning/data --results-root tuning/results`.

## Run the methods

> **In short:** each method trains on the training rows and writes estimates for the test rows to `results/<method>/<DATASET>/<N>.csv`. Then `validation.py` scores them.

### Gaussian allocation

```sh
uv run src/allocation/allocation.py --dataset {hipe,imdeld} --machines N [--components K]
```

* **`K`:** power levels per machine (idle, heating, ...). Default 3.
* **Slow** when many machines are on at once, since it tries every combination of levels.
* **Assumes** the machines switch on and off independently, and warns when two don't.

### Neural network

```sh
uv run src/neural_network/main.py --dataset {hipe,imdeld} --mode {plain,state} --machines N [--runs R] [--epochs E] [--seed S]
```

* **`plain`:** the input is the total only. **`state`:** the total and the states.
* **`--runs`:** trains R networks (5 by default) from different random starts, and averages them.
* **Output** goes to `results/neural_network/<mode>/...`.

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

> **In short:** everything but Gaussian allocation's number of levels was chosen on October. The numbers are means over HIPE groups 2 to 10.

### Training rows: 19,600, drawn at random

October error (W) of the methods that learn from the training rows. A range is two network seeds (per-range rows) or two draws (random rows). The network always takes the same number of steps: 2000 epochs on 1,960 rows, 200 on 19,600.

| Training rows | Gaussian allocation | Network, total only | Network, total and states | Proportional split |
|---|---|---|---|---|
| 490 from each of 4 power ranges (before) | 6.05 | 14.6 | 18.2 | 23.0 |
| 4,900 from each of 4 power ranges | 6.02 | 14.1 | 15.4–16.2 | 22.5 |
| 1,960 at random | 6.21 | 14.8 | 18.5 | 21.3 |
| **19,600 at random** | 6.08–6.14 | 13.3–13.6 | 12.5–13.1 | 19.5–19.6 |

* **Why at random:** the per-range draw gave the rare peaks as many rows as the common low totals, but most test seconds are low totals. It takes both more rows and the random draw for the network to gain.
* **More than 19,600 doesn't help the network** (one draw each, same number of steps): 39,200 rows give 13.3 (total only) and 12.9 (with states), 98,000 rows 13.6 and 13.8. Both are inside or above the 19,600 range.
* **Gaussian allocation** barely changes either way.
* **Where the error is left:** in seconds where several of the big ovens run together, which the total alone can't split. On group 10, December seconds whose on/off combination is not among the 1,960 earlier training rows (17%) carried 12 of allocation's 14 W and 22 of the network's 28 W. Many of those combinations never occur in November, so no number of November rows covers them.
* **December agrees** (mean over groups, W): Gaussian allocation 6.4 → 6.2, network 13.1 → 11.4 (total only) and 19.2 → 14.8 (with states), proportional split 17.2 → 16.9. With states, the network is better than total only in October but not in December.
* **Other settings** were chosen with the earlier 1,960 rows, unless noted.

### Gaussian allocation: 3 levels per machine

* **Against 1 level:** error −11 to −57% on every group in October, and −7 to −27% in December.
* **Each machine its own number of levels, picked by BIC** (a fit score that penalises extra parameters, formerly `--components auto`): barely better in October (6.07 W against 6.14 W), but worse in December (8.1 W against 6.2 W; group 10: 32.0 W against 13.4 W). So 3 levels for every machine was kept, and this one choice was not made on October alone. The option was then removed.

### Neural network

| Setting | Now | Before |
|---|---|---|
| Training | Adam, batches of 64 rows, learning rate 0.01 → 0 over 200 epochs | plain gradient descent, one row at a time |
| Hidden units | 64 | N + 1 |
| Weight decay | 0.1 (total only), 0.01 (with states) | none |
| Runs | average of 5 | the one with the lowest training loss |

Change against before, measured with the earlier 1,960 training rows and 2000 epochs:

| Input | October error | December error | October NDE | December NDE |
|---|---|---|---|---|
| Total only | −19% | −8% | −13% | −21% |
| Total and states | −60% | −29% | −76% | −32% |

* **Why weight decay:** with the total as its only input, the network over-fitted the earlier 1,960 training rows. Without decay, its NDE got worse instead of better. With 19,600 rows, 10 times less decay was still worse.
* **Why average the runs:** with the states as input, many different splits of the total fit the training data equally well, so each run picks its own. Averaging evens this out.
  * Before averaging (one-week tests), results moved with the seed. HIPE group 9: 53 ± 5 W with the states, 36 ± 1 W with the total only. IMDELD group 6, total only: 25 ± 6 kW, against 20.5 kW for guessing 0.
  * **So compare the neural network over several seeds.**

### Tried and dropped

* **The polynomial model** (from the dissertation): deleted, as it did worse than the proportional split. Each machine's power was a cubic of the total, fitted by six optimisers (particle swarm, genetic algorithm, simulated annealing, ant colony, gradient descent, Newton).
  * **December, HIPE:** 19.0 W fitted to all samples at once, 42.9 W sample by sample (the dissertation's version), against 16.9 W for the proportional split. It beat the split only on groups 4 and 8, by 0.03 W on 8.
  * **IMDELD, 6 machines:** 17.5 kW (14.5–22.3) against 20.1 kW for guessing 0 W, a win smaller than the spread between splits.
  * **Why it can't do better:** it is the neural network with each curve fixed to a cubic, and its estimates don't add up to the total. The network already does better (11.4 W).
  * **Sample by sample** solved one equation in 4 × N unknowns at each second, then averaged the answers, so the optimiser comparison measured convergence speed, not the model. Tuning the optimisers didn't help.
  * **Code:** git tag `polynomial-last`; the dissertation's own version is at `thesis-2023`.
* **Smoothing Gaussian allocation's estimates over time:** only 6% better, not worth the code. Re-tested with the 19,600 training rows as a Kalman smoother (each machine's power drifts around its mean): −6 to −8% against 1 level per machine in October, but still worse than 3 levels second by second (group 9: 9.47 W against 8.71 W).
* **Tracking each machine's power level over time:** no better. Re-tested with the 19,600 training rows (exact forward-backward, one chance per second that a machine changes level): 6.19 W at best in October, against 6.14 W. Neighbouring seconds don't reveal a machine's level any better than the second itself; they just make wrong guesses more confident.
  * **What it could gain:** told each machine's true level, Gaussian allocation's October error would fall from 6.14 to 1.6 W.
  * **Why it doesn't:** the ovens' levels are wide (the soldering oven heats at 2,980 ± 1,520 W) and change every 36 s to 5 min, so a level held from one second to the next says little.
* **Fitting Gaussian allocation's curves with another optimiser** (e.g. particle swarm instead of EM): not built. Even the best possible curves, fitted from each machine's own meter, only bring the October error from 6.14 to 5.77 W. Any optimiser working from the totals would gain less. The error comes from not knowing each machine's level, not from the curves' shape.
* **Level weights that depend on which other machines are on:** not built. In group 9's training rows, which other machines are on explains only 9–14% of the variation in each big oven's power, so there is little to gain.
* **Penalising the variance of each machine's estimate in the neural network:** worse. Meant to favour the split where each machine's power stays steady, as Gaussian allocation does. Tested in October:
  * **Group 9, total and states:** 25.2 W without it, 34.5 to 57.7 W with weights 0.001 to 1. **Total only:** 28.1 W without, 29.3 to 35.7 W with.
  * **Group 3, total and states:** 12.7 W without, 11.3 W at weight 0.001, no change at 0.01.
  * **Why:** every machine's variance counts the same, so the ovens' swings land on steady machines. One whose power barely varies went from 6.7 to 23 W.
  * Weighting each machine by its own variance would just rebuild Gaussian allocation.

## Why the states must be given

> **In short:** the methods need the on/off signals, but small delays and glitches in them cost little. Guessing them from the total doesn't work. On HIPE, a heating flag for each oven halved the error.

### Test it yourself

```sh
uv run src/validation/corrupt_states.py --dataset hipe --machines N (--lag S | --flip P) --out DIR
```

* **`--lag S`:** every state reported S seconds late.
* **`--flip P`:** each state flipped with probability P.
* Then run the methods and the scoring with `--data-root DIR`.

### What happens

HIPE, trained on November, scored on December, mean over groups 2 to 10. The training states are wrong in the same way as the test states.

| States | Gaussian allocation (W) | Proportional split (W) |
|---|---|---|
| exact | 6.2 | 16.9 |
| 10 s late | 6.4 | 16.9 |
| 60 s late | 7.3 | 17.7 |
| 1% flipped | 7.9 | 19.2 |

* **1% flipped** means each one-second reading flipped on its own, so mostly 1 s glitches, not 1% of the switch events missed.
* **Gaussian allocation still beats every baseline** given the same states, on all 9 groups, in every row.
* **A delay only matters around switches,** and December has few: 671 in group 9 over the month.
* **Milder than on the one-week release** (1 level per machine, random hours held out): there, 60 s late or 1% flipped doubled the error (10.5 W exact, 27.5 W 60 s late, 20.9 W 1% flipped).

### More than on and off: a heating flag

> **In short:** on HIPE, if the states also said when each oven is heating, Gaussian allocation's error would about halve.

**Setup:** each oven (high-temperature, soldering, vacuum) gets a heating flag: on when its own meter reads above 500 W. Optionally, the washing machine's heater too (above 1,000 W). Each flagged machine becomes two, idle and heating, each with its own 3 levels, and their estimates are added back. A one-off check, not in the code.

| States | October (W) | December (W) |
|---|---|---|
| on and off | 6.14 | 6.2 |
| plus a heating flag for the 3 ovens | 3.21 | 3.4 |
| plus the washing machine's heater | 3.03 | 3.1 |
| every machine's true level (ceiling) | 1.6 | |

* **The soldering oven's flag does most of it:** group 5, where it joins, falls from 9.1 to 3.8 W in October.
* **Groups 2–4** (only the high-temperature oven) barely change. **Group 10** in December: 13.4 → 8.8 → 6.4 W.
* **Thresholds** were read off November's power histograms, not tuned.
* **A best case:** the flag comes from the oven's own meter, so it matches the power exactly. A control system's flag would lag and match less well.
* **Specific to HIPE:** the gain comes from ovens whose heating spans a wide range that overlaps the other machines. A plant without such machines gains less, and IMDELD, whose machines switch together, nothing.
* **To use it,** give each flagged machine two state columns (idle and heating) and add their estimates back. A control system often has such a flag.

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
