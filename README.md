Table of Contents
------

* [Description](#description)
* [Directory Structure](#directory-structure)
* [Datasets](#datasets)
* [Reproduce](#reproduce)
* [Methodology notes](#methodology-notes)
* [Development](#development)
* [Licensing](#licensing)
---


Description
------
Two novel methods were developed to perform Unsupervised Low-Frequency NILM for Industrial Loads, formulated for my [master's degree dissertation in Electrical and Computer Engineering](/docs) at the [University of Coimbra](https://www.uc.pt/en).
The requirements defined the methods as unsupervised, non-event-based, compliant with low-frequency aggregate active power samples and continuously varying equipment.
The first technique uses polynomial functions, estimated through optimization algorithms, to model the active power consumption of the individual loads as a function of the aggregate active power (EMUPF).
The second algorithm consists of an unsupervised neural network (UNN) that estimates the active power of the equipment based on the optimization of an objective function instead of solving a classification problem with labelled data.
The HIPE and the IMDELD datasets were preprocessed and used to train and validate the algorithms.
A third method was added after the dissertation: Gaussian allocation models each machine's power while ON as an independent Gaussian, fits the means and variances from the aggregate and the on/off states alone, and gives each machine its posterior mean.


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
    ├── LICENSE
    ├── README.md
    ├── pyproject.toml          # Python dependencies, locked in uv.lock
    └── uv.lock


Datasets
------
Neither dataset is redistributed here. Obtain the raw data under each dataset's own terms and place it in `data/raw`; the preprocessing scripts generate everything else (see [Reproduce](#reproduce)).

* IMDELD, Industrial Machines Dataset for Electrical Load Disaggregation (Martins et al.), IEEE DataPort: https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation
  Expected: `data/raw/IMDELD/Equipment/*.csv` (eight machines, columns `timestamp, active_power, reactive_power, apparent_power, current, voltage`), `data/raw/IMDELD/pelletizer-subcircuit.csv`, `data/raw/IMDELD/millingmachine-subcircuit.csv`.
* HIPE, High-resolution Industrial Production Energy dataset (Bischof et al.), KIT: https://www.energystatusdata.kit.edu/hipe.php
  `uv run src/preprocessing/fetch_hipe.py` downloads the one-week release (109 MB, checksum verified) and unpacks its ten machine files into `data/raw/HIPE/Equipment` (`SensorDateTime`, `P_kW`, ...); the first one alphabetically is always off and is dropped.

Processed layout, the same for both datasets: `data/processed/<DATASET>/<N>/{aggregate,states,equipment}{,_training,_validation}.csv`, N the number of machines; the files without a suffix are the unsplit tables.
Every file starts with a `timestamp` column; the aggregate's power column is `active_power`, then one column per machine. HIPE is in kW, IMDELD in W.
* IMDELD: N = 6 is machines 1, 2, 3, 4, 7 and 8 in alphabetical file order, N = 8 all of them.
* HIPE: N = 2..9 is the first N machines, the aggregate their synthetic sum.


Reproduce
------
The Python code runs with [uv](https://docs.astral.sh/uv/): `uv run` creates the environment from `uv.lock` on first use. Every Python folder has a self-check, e.g. `uv run src/validation/test_validation.py`.

1. Get the raw data: `uv run src/preprocessing/fetch_hipe.py` for HIPE, IMDELD by hand (see Datasets).
2. Preprocess: `uv run src/preprocessing/imdeld.py` (add `--equipment 1,2,3,4,5,6,7,8` for the 8-machine set) and `uv run src/preprocessing/hipe.py`.
3. EMUPF (CMake >= 3.20, C++20 compiler, GCC 13 tested, OpenMP optional): `cmake -S src/optimization -B build && cmake --build build -j && ctest --test-dir build`; then run `estimate` / `validate` as described in [src/optimization/README.md](src/optimization/README.md).
4. UNN: `uv run src/deep_learning/main.py --dataset {hipe,imdeld} --mode {plain,state,fourier} --machines N [--runs R] [--epochs E] [--seed S]`. Output: `results/deep_learning/<mode>/<DATASET>/<N>.csv`.
5. Gaussian allocation: `uv run src/allocation/allocation.py --dataset {hipe,imdeld} --machines N`. It trains on every unsplit sample outside the validation split, which needs no per-machine power. Output: `results/allocation/<DATASET>/<N>.csv`.
6. Hart-inspired baseline: `uv run src/hart_inspired/hart_inspired.py --dataset hipe --machines 9`. It runs on the unsplit tables and uses the true on/off states, so it is an oracle reference, not an unsupervised method. Output: `results/hart_inspired/<DATASET>/<N>.csv`.
7. Validation: `uv run src/validation/validation.py [--plots DIR]`. It pairs every `results/<method>/<DATASET>/<N>.csv` with `data/processed/<DATASET>/<N>/equipment_validation.csv` (`equipment.csv` for the Hart-inspired baseline).

The preprocessing, baseline and validation were ported from MATLAB; the MATLAB versions used in the dissertation are in the git history.


Methodology notes
------
* IMDELD signals are smoothed with a 25-minute moving mean; HIPE is not smoothed.
* The HIPE training/validation aggregate is the synthetic sum of the selected machines, not the main meter.
* On/off thresholds: flat 5 W for IMDELD; > 0 after spline fitting for HIPE.
* The train/validation split takes the same number of samples (at most 700) from each aggregate bin and splits each bin 70/30 with a fixed seed.


Development
------
CI runs the C++ tests, every Python self-check and the linters below; run them locally before pushing.
* Python: `uv run ruff format` and `uv run ruff check` (settings in `pyproject.toml`).
* C++: `clang-format -i src/optimization/*.h src/optimization/*.cpp`, and `clang-tidy -p build --extra-arg=-fno-openmp src/optimization/*.cpp` after configuring with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` (settings in `.clang-format` and `.clang-tidy`).


Licensing
------
Copyright © 2023 [Daniel Torres](https://github.com/danctorres).<br />
This project is [CC BY-NC-SA 4.0](LICENSE) licensed. The datasets keep their own terms.
