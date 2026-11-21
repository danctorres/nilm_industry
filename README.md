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


Directory Structure
------
    .
    ├── data
    │   ├── raw                 # Original datasets (not versioned, obtain separately)
    │   ├── interim             # Intermediate data
    │   └── processed           # Preprocessed data (see Datasets)
    ├── docs                    # Documentation and report files
    ├── results                 # Results from the methods developed
    ├── src                     # Source files
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
Neither dataset is redistributed here. Obtain the raw data under each dataset's own terms and place it in `data/raw`.
The processed CSVs in `data/processed` are Git LFS pointers or outputs of older code; regenerate them with the preprocessing scripts (see [Reproduce](#reproduce)).

* IMDELD, Industrial Machines Dataset for Electrical Load Disaggregation (Martins et al.), IEEE DataPort: https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation
  Expected: `data/raw/IMDELD/Equipment/*.csv` (eight machines, columns `timestamp, active_power, reactive_power, apparent_power, current, voltage`), `data/raw/IMDELD/pelletizer-subcircuit.csv`, `data/raw/IMDELD/millingmachine-subcircuit.csv`.
* HIPE, High-resolution Industrial Production Energy dataset (Bischof et al.), KIT: https://www.energystatusdata.kit.edu/hipe.php
  Expected: `data/raw/HIPE/Equipment/*.csv`, the ten one-week machine files (`SensorDateTime`, `P_kW`); the first one alphabetically is always off and is dropped.

Processed layout:
* `data/processed/IMDELD/data_{6,8}_equipment/{aggregate,on_off,equipment}_{training,validation}.csv` (the 6-machine set is machines 1, 2, 3, 4, 7 and 8 in alphabetical file order)
* `data/processed/HIPE/1_week/{aggregate,state,equipment}_{training,validation}/..._N.csv`


Reproduce
------
The Python code runs with [uv](https://docs.astral.sh/uv/): `uv run` creates the environment from `uv.lock` on first use. Every Python folder has a self-check, e.g. `uv run src/validation/test_validation.py`.

1. Get the raw data (see Datasets).
2. Preprocess: `uv run src/preprocessing/imdeld.py` (add `--equipment 1,2,3,4,5,6,7,8` for the 8-machine set) and `uv run src/preprocessing/hipe.py`.
3. EMUPF (CMake >= 3.20, C++20 compiler, GCC 13 tested, OpenMP optional): `cmake -S src/optimization -B build && cmake --build build -j && ctest --test-dir build`; then run `estimate` / `validate` as described in [src/optimization/README.md](src/optimization/README.md).
4. UNN: `uv run src/deep_learning/main.py --dataset {hipe,imdeld} --mode {plain,state,fourier} --machines N [--runs R] [--epochs E] [--seed S]`. Output: `results/deep_learning/<DATASET>/[1_week/]{,fourier/,states/}estimated_active_power_<N>.csv`.
5. Hart-inspired baseline: `uv run src/hart_inspired/hart_inspired.py`. It uses the true on/off states, so it is an oracle reference, not an unsupervised method.
6. Validation: `uv run src/validation/validation.py [--plots DIR]`. It pairs every `estimated_active_power_<N>.csv` with the ground truth for N machines and skips methods that have no results yet.

The preprocessing, baseline and validation were ported from MATLAB; the MATLAB versions used in the dissertation are in the git history.


Methodology notes
------
* Ground truth is smoothed with a 25-minute moving mean.
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
