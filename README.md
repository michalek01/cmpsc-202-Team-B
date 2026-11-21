# cmpsc-202-Team-B
Kallan Fuchs, 
Isaac Michalek, 
Issei Hasegawa

## Project 3: Navigating the Sea
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. Determine the path that maximizes the total accumulated biomass density score.

See the [planning document](planning.md) for the problem formulation, algorithm design, and complexity analysis, and the [evaluation document](evaluation.md) for the testing and benchmarking results.

## Running the Code

From the `src` folder:

- `python3 -m unittest tests -v` runs the tests.
- `python3 benchmark.py` times both algorithms and writes the results to `assets/empirical_results.csv`.
- `plots.ipynb` reads that file and saves the plots to `assets/`. It needs numpy, pandas, seaborn, and matplotlib.
