Table of Contents
------

* [Description](#description)
* [Directory Structure](#directory-structure)
* [Relevant Resources](#relevant-resources)
* [Licensing](#licensing)
---


Description
------
Two novel methods were developed to perform Unsupervised Low-Frequency NILM for Industrial Loads, formulated for my master's degree dissertation in Electrical and Computer Engineering at the [University of Coimbra](https://www.uc.pt/).
The requirements defined the algorithms as unsupervised, non-event-based, compliant with low-frequency aggregate active power samples and continuously varying equipment.
The first algorithm uses polynomial functions, estimated through optimization algorithms, to model the active power consumption of the individual loads as a function of the aggregate active power (EMUPF).
The second algorithm consists of an unsupervised neural network (UNN) that estimates the active power of the equipment based on the optimization of an objective function instead of solving a classification problem with labelled data.
The UNN algorithm was trained and tested with two sets of inputs, aggregate active power and equipment state samples, and aggregate active power samples passed through a Fourier feature mapping.
The High-resolution Industrial Production Energy (HIPE) and the Industrial Machines Dataset for Electrical Load Disaggregation (IMDELD) datasets were preprocessed and used to train and validate the algorithms.


Directory Structure
------
    .
    ├── data
    │   ├── raw                 # Original dataset
    │   ├── interim             # Intermediate data
    │   └── processed           # Preprocessed data
    ├── docs                    # Documentation and report files
    ├── results                 # Results from the methods developed
    ├── src                     # Source files
    │   ├── deep_learning       # UNN method code developed in Python
    │   ├── hart_inspired       # Simple Hart inspired method developed in MATLAB
    │   ├── optimization        # EMUPF method developed in C++
    │   ├── preprocessing       # MATLAB code for the preprocessing of the datasets
    │   └── validation          # MATLAB code for the validation of the methods' results
    ├── LICENSE
    └── README.md


Relevant resources
------
* IMDELD dataset: https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation
* HIPE dataset: https://www.energystatusdata.kit.edu/hipe.php

Licensing
------
Copyright © 2023 [Daniel Torres](https://github.com/danctorres).<br />
This project is [MIT](https://github.com/danctorres/nilm_disseration/blob/main/LICENSE) licensed.