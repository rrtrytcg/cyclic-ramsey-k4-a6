# Some results on small ordered and cyclic Ramsey numbers

This is a GitHub repository containing the source code together with some supplementary material for the paper:

- N. Bašić, I. Damnjanović, D. Stevanović and I. Stošić, Some results on small ordered and cyclic Ramsey numbers, 2026, #TODO.

## Repository Structure

```
.
├── include/
├── src/
│   ├── sat_solving/
│   │   ├── cnf_generator.cpp
│   │   ├── cnf_generator.py
│   │   ├── get_binaries.sh
│   │   ├── solve_instance.sh
│   │   ├── find_number.sh
│   │   ├── find_number_grid.sh
│   │   └── kissat_output_parser.py
│   ├── score_computation/
│   └── rlgt_trainer.py
├── kissat_output/
├── parsed_graphs/
└── generated_tables/
```

- [`include`](./include) contains the `C/C++` header files with various auxiliary functions to be later used.
- [`src`](./src) contains the source code for all the main functions.
  - [`src/sat_solving`](./src/sat_solving) contains the source code used to create and execute SAT instances, as well as parse the obtained results.
    - [`src/sat_solving/cnf_generator.cpp`](./src/sat_solving/cnf_generator.cpp) is a `C++` program that generates SAT instances.
    - [`src/sat_solving/cnf_generator.py`](./src/sat_solving/cnf_generator.py) is a `Python` program that generates SAT instances.
    - [`src/sat_solving/get_binaries.sh`](./src/sat_solving/get_binaries.sh) is an auxiliary `bash` script used by the other `bash` scripts which ensures that all the necessary binaries are present.
    - [`src/sat_solving/solve_instance.sh`](./src/sat_solving/solve_instance.sh) is a `bash` script that solves a given SAT instance.
    - [`src/sat_solving/find_number.sh`](./src/sat_solving/find_number.sh) is a `bash` script that computes a given ordered or cyclic Ramsey number.
    - [`src/sat_solving/find_number_grid.sh`](./src/sat_solving/find_number_grid.sh) is a `bash` script that computes a grid of ordered or cyclic Ramsey number for the same pair of classes of graphs. This corresponds to a table from Section 4.
    - [`src/sat_solving/kissat_output_parser.py`](./src/sat_solving/kissat_output_parser.py) is a `Python` script that parses all the obtained Kissat output files located in the [`kissat_output`](./kissat_output) folder. As a result, the graphs which yield all the lower bounds are obtained and stored in the [`parsed_graphs`](./parsed_graphs) folder, while the automatically generated LaTeX tables are stored in the [`generated_tables`](./generated_tables) folder.
  - [`src/score_computation`](./src/score_computation) contains the `Python` and `C++` files that compute all the Ramsey score functions to be used by the RL training script.
  - [`src/rlgt_trainer.py`](./src/rlgt_trainer.py) contains the RLGT-based training script that finds lower bounds on ordered or cyclic Ramsey numbers.
- [`kissat_output`](./kissat_output) contains all the output files produced by running Kissat on the generated SAT instances.
- [`parsed_graphs`](./parsed_graphs) contains the graphs extracted from the Kissat output files using the `Python` parsing script. These graphs are stored in the `graph6` format and provide lower bounds for the computed ordered and cyclic Ramsey numbers.
- [`generated_tables`](./generated_tables) contains automatically generated LaTeX code used to produce the tables in Section 4.

## Graph Abbreviations

In all the subfolders of [`kissat_output`](./kissat_output), [`parsed_graphs`](./parsed_graphs) and [`generated_tables`](./generated_tables), the following abbreviations are used:
- `pmon` is the monotone path.
- `palt` is the alternating path.
- `pralt` is the reverse alternating path.
- `cmon` is the monotone cycle.
- `ssc` is the start-central star.
- `k` is the complete graph.
- `mnest` is the nested matching.
- `pqmon` is the quasi-monotone path (used only in Example 2.5).
- `ord` refers to the ordered Ramsey number problem.
- `cyc` refers to the cyclic Ramsey number problem.

## Usage Instructions

All `bash` scripts should be run from the containing folder and they can only be executed on Linux or MacOS. Moreover, the only difference on these two operating systems is that the `timeout` command is used on Linux, while `gtimeout` is instead used on MacOS. This additional command can be installed on MacOS as follows:
```
brew install coreutils
```

The `Python` scripts [`src/sat_solving/cnf_generator.py`](./src/sat_solving/cnf_generator.py) and [`src/rlgt_trainer.py`](./src/rlgt_trainer.py) should be run from the root folder using `poetry` as follows:
```
poetry run python src/sat_solving/cnf_generator.py
poetry run python src/rlgt_trainer.py
```

On the other hand, the `Python` script [`src/sat_solving/kissat_output_parser.py`](./src/sat_solving/kissat_output_parser.py) depends on `SageMath` and should therefore be run as follows:
```
sage src/sat_solving/kissat_output_parser.py
```
using the `SageMath` interpreter.

In addition, before the `Python` script [`src/rlgt_trainer.py`](./src/rlgt_trainer.py) can be used, the required `Cython` wrapper should be configured as follows:
```
cd src/score_computation
poetry run python setup.py build_ext --inplace
```

We mention that the Ramsey score computation may not work on MacOS.

## Citation

If you use this code in your research, please cite the associated paper:

- N. Bašić, I. Damnjanović, D. Stevanović and I. Stošić, Some results on small ordered and cyclic Ramsey numbers, 2026, #TODO.
