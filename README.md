Table of Contents
------

* [Description](#description)
* [Directory Structure](#directory-structure)
* [Datasets](#datasets)
* [Reproduce](#reproduce)
* [Methodology notes](#methodology-notes)
* [Licensing](#licensing)
---


Description
------
Two novel methods were developed to perform Unsupervised Low-Frequency NILM for Industrial Loads, formulated for my [master's degree dissertation in Electrical and Computer Engineering](/docs) at the [University of Coimbra](https://www.uc.pt/en).
The requirements defined the methods as unsupervised, non-event-based, compliant with low-frequency aggregate active power samples and continuously varying equipment.
The first technique uses polynomial functions, estimated through optimization algorithms, to model the active power consumption of the individual loads as a function of the aggregate active power (EMUPF).
The second algorithm consists of an unsupervised neural network (UNN) that estimates the active power of the equipment based on the optimization of an objective function instead of solving a classification problem with labelled data.
The HIPE and the IMDELD datasets were preprocessed and used to train and validate the algorithms.
A third method was added after the dissertation: Gaussian allocation models each machine's power while ON as an independent mixture of Gaussians (an oven idling or heating, say), fits it from the aggregate and the on/off states alone, and gives each machine its posterior mean.

Every method takes each machine's on/off state as an input, and here those states come from the per-machine meters. The methods therefore split the aggregate among machines known to be ON, which is easier than unsupervised NILM, where the states must be found from the aggregate too. They suit plants where each machine's on/off status comes from its own signal, such as a PLC output, accurate to about 10 s. See [Methodology notes](#methodology-notes) for what each method can and cannot tell apart, and why the states cannot simply be inferred from the aggregate.


Directory Structure
------
    .
    ├── data                    # Not versioned
    │   ├── raw                 # Original datasets, obtain separately (see Datasets)
    │   └── processed           # Written by src/preprocessing (see Datasets)
    ├── docs                    # Documentation and report files
    ├── results                 # Not versioned, written by the methods: <method>/<DATASET>/<N>.csv
    ├── src                     # Source files
    │   ├── allocation          # Gaussian allocation, added after the dissertation, in Python
    │   ├── deep_learning       # UNN method developed in Python
    │   ├── hart_inspired       # Hart-inspired baseline developed in Python
    │   ├── optimization        # EMUPF method developed in C++
    │   ├── preprocessing       # Python code for the preprocessing of the datasets
    │   └── validation          # Python code for the validation of the methods' results
    ├── tuning                  # Not versioned: data/ and results/ of the HIPE tuning copy (see Reproduce)
    ├── LICENSE
    ├── README.md
    ├── pyproject.toml          # Python dependencies, locked in uv.lock
    └── uv.lock


Datasets
------
Neither dataset is redistributed here. Obtain the raw data under each dataset's own terms and place it in `data/raw`; the preprocessing scripts generate everything else (see [Reproduce](#reproduce)).

* IMDELD, Industrial Machines Dataset for Electrical Load Disaggregation (Martins et al.), IEEE DataPort: https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation
  Downloading needs a free IEEE account. From the dataset's file list:
  * the zip with all appliances (`Appliances.zip`): unpack its eight machine files into `data/raw/IMDELD/Equipment`;
  * "Pelletizer SubCircuit", the aggregate meter: save it as `data/raw/IMDELD/pelletizer-subcircuit.csv`;
  * "Milling Machines SubCircuit", only for the 8-machine set: save it as `data/raw/IMDELD/millingmachine-subcircuit.csv`.
* HIPE, High-resolution Industrial Production Energy dataset (Bischof et al.), KIT: https://www.energystatusdata.kit.edu/hipe.php
  `uv run src/preprocessing/fetch_hipe.py` downloads the three-month release, 1 Oct 2017 to 1 Jan 2018, from [Zenodo](https://doi.org/10.5281/zenodo.14054902) (1.33 GB, 30.6 GB unpacked, checksum verified) and unpacks its ten machine files into `data/raw/HIPE/Equipment` (`SensorDateTime`, `P_kW`, ...) and the main meter, `MainTerminal`, into `data/raw/HIPE`.

Processed layout, the same for both datasets: `data/processed/<DATASET>/<N>/{aggregate,states,equipment}{,_training,_validation}.csv`, N the number of machines; the files without a suffix are the unsplit tables.
Every file starts with a `timestamp` column; the aggregate's power column is `active_power`, then one column per machine. HIPE is in kW, IMDELD in W.
* IMDELD: N = 6 is machines 1, 2, 3, 4, 7 and 8 in alphabetical file order, N = 8 all of them.
* HIPE: N = 2..9 is machines 2 to N + 1 in alphabetical file order, and N = 10 adds machine 1, the ChipPress, which runs in November and December only (always off in the dissertation's one-week release, hence last). The aggregate is the synthetic sum of the N machines.


Reproduce
------
The Python code runs with [uv](https://docs.astral.sh/uv/): `uv run` creates the environment from `uv.lock` on first use. Every Python folder has a self-check, e.g. `uv run src/validation/test_validation.py`.

1. Get the raw data: `uv run src/preprocessing/fetch_hipe.py` for HIPE, IMDELD by hand (see Datasets).
2. Preprocess: `uv run src/preprocessing/imdeld.py` (add `--equipment 1,2,3,4,5,6,7,8` for the 8-machine set) and `uv run src/preprocessing/hipe.py` (about 30 min, 8 GB of output).
3. EMUPF (CMake >= 3.20, C++20 compiler, GCC 13 tested, OpenMP optional): `cmake -S src/optimization -B build && cmake --build build -j && ctest --test-dir build`; then run `estimate` / `validate` as described in [src/optimization/README.md](src/optimization/README.md).
4. UNN: `uv run src/deep_learning/main.py --dataset {hipe,imdeld} --mode {plain,state} --machines N [--runs R] [--epochs E] [--seed S]`. It trains with Adam on batches of 64 rows, the learning rate falling from 0.01 to 0 over 2000 epochs, with 64 hidden units, chosen on October against the per-sample SGD and n + 1 hidden units first used: averaged over HIPE 2 to 10, the October MAE falls by half in state mode (NDE by 60%) and by 16% in plain mode, whose NDE rises by a quarter, as the wider network fits the small training split more closely. On December the MAE falls by 25% in state mode and 9% in plain mode. Output: `results/deep_learning/<mode>/<DATASET>/<N>.csv`.
5. Gaussian allocation: `uv run src/allocation/allocation.py --dataset {hipe,imdeld} --machines N [--components K]`. K, the Gaussians per machine, is 3 by default, chosen on October: on HIPE 4 to 10 it lowers the October MAE by 7 to 32% against K = 1, a single Gaussian per machine, the method as first added, and the December MAE by 5 to 24%; K = 1 stays slightly better on HIPE 2 and 3. Its cost grows as K to the number of machines ON at once. It trains on the training split, the same rows as EMUPF and UNN. It assumes the machines switch independently and warns when two switch together, as on IMDELD, where no method can tell their power apart. Output: `results/allocation/<DATASET>/<N>.csv`.
6. Hart-inspired baseline: `uv run src/hart_inspired/hart_inspired.py --dataset hipe --machines 9`. It runs on the unsplit tables and uses the true on/off states, so it is an oracle reference, not an unsupervised method. Output: `results/hart_inspired/<DATASET>/<N>.csv`.
7. Validation: `uv run src/validation/validation.py [--plots DIR]`. It pairs every `results/<method>/<DATASET>/<N>.csv` with `data/processed/<DATASET>/<N>/equipment_validation.csv`; the Hart-inspired baseline is scored on the same validation rows of its whole-recording estimates, with the share of ON samples it could estimate. Three baselines that see only the aggregate and the states are scored next to every set: zero, the aggregate split equally among the ON machines, and split in proportion to each machine's mean power fitted to the training split. The output ends with one line per method: MAE over all machines and the pooled NDE.

To tune a method on HIPE, run steps 3 to 7 on the tuning copy `hipe.py` writes, which validates on October instead of December: add `--data-root tuning/data` and `--results-root tuning/results/<method>` to a method (`tuning/results` for `validation.py`; for EMUPF, the paths under `tuning/data/HIPE/<N>`). Report on December only what was chosen on October.

The preprocessing, baseline and validation were ported from MATLAB; the MATLAB versions used in the dissertation are in the git history.


Methodology notes
------
* IMDELD signals are smoothed with a 25-minute moving mean that restarts after gaps between kept days; HIPE is not smoothed.
* HIPE timestamps are in UTC, so the recording runs on through the end of summer time on 29 Oct 2017. Rows inside a gap of more than 300 s between two raw samples of any machine are dropped from every machine and set: 8.5 min in every machine on 10 Nov 2017 and 21 h in the VacuumOven on 14 and 15 Dec.
* The HIPE training/validation aggregate is the synthetic sum of the selected machines, not the main meter: the ten machines draw only 4% of the main meter's energy (0.58 kW against 14.0 kW on average), and the rest, plant load that follows the working day from about 8 kW at night to 20 kW at midday, would go to whichever machines are ON.
* On/off thresholds: flat 5 W for IMDELD; > 0 after spline fitting for HIPE.
* HIPE is split by month, in UTC: October tunes (`tuning/data`), November trains and December reports (`data/processed`); the seed only changes which November rows training draws. IMDELD holds out whole days, 30% of them drawn with a fixed seed. Validation scores every row of its month or days; training draws the same number of rows (at most 490) from each aggregate bin of the other blocks, six bins of one standard deviation, the outer two open-ended so training includes the peaks. Rows near a cut are left out (300 s for HIPE, the longest gap between raw samples it keeps; 750 s for IMDELD, half the smoothing window), so no two splits share raw samples.
* The numbers in the notes below and in the last table were measured on the one-week HIPE release (23 to 30 Oct 2017), split into random hours, before `fetch_hipe.py` moved to the three-month one, with a single Gaussian per machine for Gaussian allocation and per-sample SGD for UNN.
* UNN with `--mode state` is not identifiable: with the states as input, any split of the aggregate among the ON machines minimises its loss, so its estimates change with the seed. On HIPE/9, seeds 0 to 2 give MAE 0.053 ± 0.005 kW in state mode and 0.036 ± 0.001 kW in plain mode. On IMDELD/6 both modes change with the seed (plain: 25 ± 6 kW, against 20.5 kW for the zero baseline), so report UNN over several seeds.
* EMUPF fitted sample by sample solves one equation in `4 x machines` unknowns per sample and averages the solutions (see [src/optimization/README.md](src/optimization/README.md#limitation-of-the-method)); `estimate --joint` fits one well-posed objective and is the version to compare.
* On IMDELD the machines switch on and off together (state correlations 0.93 to 1.00), and 96% of the samples have every machine ON or every machine OFF, so no method that relies on the states can tell their power apart, and grouping the machines that switch together leaves one group; compare against the baselines before reading anything into the IMDELD numbers.
* The IMDELD aggregate is a real meter and carries 2 to 3% of load from unmetered equipment, which the methods must assign to some machine.
* The methods need exact states. `uv run src/validation/corrupt_states.py --dataset hipe --machines N (--lag S | --flip P) --out DIR` writes a copy of a set with every state reported S seconds late or each entry flipped with probability P; run the methods and the validation with `--data-root DIR`. Averaged over HIPE 2 to 9, Gaussian allocation's MAE grows from 10.5 W with the true states to 11.2 W with a 10 s lag, 27.5 W with a 60 s lag and 20.9 W with 1% of the entries flipped, against 31.2 W for the proportional baseline with the true states. With a 60 s lag it beats the best baseline, given the same states, in 4 of the 8 sets. Inferring the states from the aggregate would do worse: in HIPE/9, the aggregate changes by more than 0.05 kW over 240 s 2,213 times, and only 322 of these are within 240 s of a machine switching on or off (leaving out the 8 W machine, which switches 2,215 times); the rest are machines changing load while ON.

HIPE validation MAE in W over all machines from `validation.py`: trained on November, scored on December, every choice made on October (preprocessing `--seed 1`, UNN `--seed 0`, EMUPF `--seed 1`):

| Method | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Gaussian allocation | 4.0 | 3.3 | 2.1 | 9.2 | 7.2 | 6.3 | 6.0 | 5.9 | 13.7 | 6.4 |
| Gaussian allocation, one Gaussian per machine | 3.6 | 3.2 | 2.8 | 9.7 | 8.4 | 7.6 | 6.8 | 6.8 | 15.1 | 7.1 |
| UNN plain | 7.5 | 9.6 | 11.7 | 20.4 | 16.5 | 22.2 | 19.0 | 17.8 | 42.9 | 18.6 |
| UNN state | 19.1 | 20.7 | 20.9 | 22.4 | 13.1 | 34.6 | 13.5 | 16.9 | 29.3 | 21.2 |
| EMUPF per sample | 72.9 | 60.2 | 48.1 | 58.0 | 47.8 | 43.7 | 38.9 | 34.9 | 47.7 | 50.2 |
| EMUPF `--joint` | 10.3 | 11.3 | 11.4 | 21.1 | 19.6 | 21.2 | 18.9 | 22.9 | 57.4 | 21.6 |
| Hart-inspired | 72.7 | 54.9 | 46.5 | 47.7 | 40.2 | 46.4 | 43.2 | 41.2 | 66.5 | 51.0 |
| Baseline: zero | 73.2 | 55.3 | 47.4 | 48.4 | 40.7 | 46.6 | 43.4 | 41.3 | 66.7 | 51.4 |
| Baseline: equal split | 20.6 | 24.8 | 27.5 | 30.9 | 25.9 | 30.4 | 27.3 | 26.1 | 42.1 | 28.4 |
| Baseline: proportional | 11.6 | 11.7 | 14.9 | 18.7 | 14.2 | 20.4 | 17.3 | 15.7 | 33.3 | 17.5 |

Gaussian allocation beats every other method and baseline on every set, one Gaussian per machine doing slightly better on HIPE 2 and 3. UNN plain and EMUPF `--joint` beat the proportional baseline on HIPE 2 to 4, UNN state on 6, 8 and 10. HIPE 10 is the hardest: the ChipPress, which runs in November and December only, adds large loads that October never shows.

On the one-week release, validation MAE in kW over all machines, mean ± standard deviation over three splits (preprocessing `--seed 1`, the default, then 2 and 3; UNN `--seed 0`, EMUPF `--seed 1`):

| Method | HIPE, 9 | IMDELD, 6 | IMDELD, 8 |
|---|---|---|---|
| Gaussian allocation | 0.021 ± 0.014 | 37.6 ± 1.5 | 31.7 ± 3.2 |
| UNN plain | 0.039 ± 0.019 | 20.9 ± 2.9 | 22.8 ± 0.8 |
| UNN state | 0.055 ± 0.015 | 26.6 ± 1.9 | 24.3 ± 3.4 |
| EMUPF per sample | 0.047 ± 0.014 | 22.9 ± 0.8 | 18.6 ± 0.4 |
| EMUPF `--joint` | 0.043 ± 0.022 | 19.4 ± 1.9 | 17.3 ± 3.5 |
| Hart-inspired (estimates 7 to 17% of the ON samples) | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: zero | 0.055 ± 0.016 | 19.9 ± 0.8 | 20.4 ± 0.4 |
| Baseline: equal split | 0.039 ± 0.016 | 24.1 ± 1.0 | 19.0 ± 0.2 |
| Baseline: proportional | 0.036 ± 0.012 | 37.4 ± 2.2 | 32.5 ± 3.5 |

The spread is mostly the split: which hours or days are held out. On HIPE, Gaussian allocation beats the best baseline in all 24 pairs of machine count (2 to 9) and split; UNN plain does in 5, UNN state and EMUPF `--joint` in 3, EMUPF per sample in none. On IMDELD, EMUPF `--joint` beats the best baseline in 4 of the 6 pairs, by less than the spread between splits, and the best method changes with the split.

Licensing
------
Copyright © 2023 [Daniel Torres](https://github.com/danctorres).<br />
This project is [CC BY-NC-SA 4.0](LICENSE) licensed. The datasets keep their own terms.
