Low-Frequency Unsupervised Non-Intrusive Load Monitoring for Industrial Loads
============================

> Repo of the code and documentation related to my master's degree dissertation in Electrical and Computer Engineering at the University of Coimbra.

> The dissertation titled "Low-Frequency Unsupervised Non-Intrusive Load Monitoring for Industrial Loads" focuses on developing innovative techniques for monitoring industrial loads.

> The main contribution of the dissertation is the development of a novel method for nilm, called Multi-Modal Functional Matrix Factorization with Numerical and Metaheuristic Optimization and with Kalman Filtering.

> Code developed in MATLAB, Python and C++.

### Structure:
```
.
├── build                   # Compiled files
├── data
│   ├── raw                 # Imdeld dataset
│   ├── interim             # Intermediate data
│   └── processed           # Final dataset for modeling
├── docs                    # Documentation files
├── reports					
│   └── figures             # Generated figures to be used in reporting 
├── src                     # Source files
│   ├── preprocessing       # Code to analyze the dataset, cleaning, transforming and organizing the data in a format that is suitable for the algorithm
│   ├── nilm                # Complete algorithm
│   └── optimization        # Optimization algorithms (estimating the coefficients of the functions in the W matrix)
├── test                    # Automated tests
├── tools                   # Tools and utilities
├── LICENSE
└── README.md
```

### How to install and set up:
```
• Clone the repo.
• Download the imdeld dataset from IEEEDataPort into the data/raw folder.
```

### How to use the repo:
> ToDo


### Link to relevant resources:
> Imdeld dataset: https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation
