# Artifact Evaluation

The paper presents three main claims regarding LEOCraft:

1. **LEOCraft is a flow-level LEO network simulator** that can rapidly assess a given LEO constellation design's throughput, coverage, and stretch/latency with specified ground stations and traffic matrices.

2. **LEOCraft employs a search space heuristic** that significantly accelerates the optimization of constellation design for specific ground stations and traffic matrices, especially when compared to naive approaches.

3. **LEOCraft can evaluate and simulate designs for multi-shell** LEO constellations and inter-shell inter-satellite link connectivity.

4. **LEOCraft features an interactive visualization framework** that allows for an intuitive understanding and examination of LEO network designs and their dynamics.

To reproduce the results, follow the steps given below.

# Overview
- [Getting Started](#getting-started)
    - [Setup the Simulation Environment](#setup-the-simulation-environment)
    - [Get the Academic License for Gurobi Optimizer](#get-the-academic-license-for-gurobi-optimizer)
    - [Test the Simulation Environment](#test-the-simulation-environment)
- [Regenerating the Results in the Paper](#regenerating-the-results-in-the-paper)
    - [Exploring the Search Space](#exploring-the-search-space)
    - [Constellation Design Optimization](#constellation-design-optimization)
    - [Exploring Mult-Shell Design](#exploring-mult-shell-design)
    - [Evaluate Inter-shell ISL Connectivity](#evaluate-inter-shell-isl-connectivity)
    - [Visualization of LEO Constellations](#visualization-of-leo-constellations)


## Getting Started

### Setup the Simulation Environment

Clone the LEOCraft repository.

```bash
git clone https://github.com/suvambasak/LEOCraft.git
```

Change the directory.

```bash
cd LEOCraft
```

Create a conda environment from [environment.yml](/tools/environment.yml) or [environment_macOS.yml](/tools/environment_macOS.yml).

```bash
conda env create -f tools/environment.yml
```
or
```bash
conda env create -f tools/environment_macOS.yml
```

Activate `leocraft` environment.

```bash
conda activate leocraft
```

---




### Get the Academic License for Gurobi Optimizer

Since `LEOCraft` is a flow-level simulator, it uses [Gurobi Optimizer](https://www.gurobi.com/) to solve the linear program of throughput maximization. To set Gurobi Optimizer:

- Extract the license tools [licensetools12.0.1_linux64.tar.gz](/tools/licensetools12.0.1_linux64.tar.gz) or download the [license tools](https://support.gurobi.com/hc/en-us/articles/360059842732-How-do-I-set-up-a-license-without-installing-the-full-Gurobi-package) based on your platform to the binary `grbgetkey`.

- [Sign up](https://portal.gurobi.com/iam/login/) and generate free [Named-User Academic](https://portal.gurobi.com/iam/licenses/request) license.

- To save the license on your system, execute the following.

```bash
./grbgetkey <LICENSE_KEY>
```

Enter and store the `gurobi.lic` file in the home directory.

```bash
info  : grbgetkey version 12.0.1, build v12.0.1rc0
info  : Platform is linux64 (linux) - "Linux Mint 22.1"
info  : Contacting Gurobi license server...
info  : License file for license ID XXXXXXX was successfully retrieved
info  : License expires at the end of the day on XXXX-XX-XX 
info  : Saving license file...

In which directory would you like to store the Gurobi license file?
[hit Enter to store it in /home/suvam]:
```


---

### Test the Simulation Environment

Export the `LEOCraft` project path in the shell, which will allow seamless execution of scripts.


```bash
export PYTHONPATH=$(pwd)
```

Or, for instance, if the repository is cloned at `/mnt/Storage/Projects/LEOCraft`


```bash
export PYTHONPATH="/mnt/Storage/Projects/LEOCraft"
```

To validate the simulation environment setup, execute [example_starlink.py](/examples/example_starlink.py), which simulates the Starlink multi-shell LEO constellation.

```bash
python examples/example_starlink.py
```

The `LEOCraft` setup is successful if you see something like this.

```bash
[LEOConstellation] Building ground stations...
[LEOConstellation] Building shells...
[LEOConstellation] Building ground to satellite links...                
[LEOConstellation] GSLs generated in: 0.08m                             
[LEOConstellation] Adding satellites into network graph...
[LEOConstellation] Adding ISLs into network graph...
[LEOConstellation] Routes generated in: 2.2m                            

[Throughput] Building throughput...
[Throughput] Computing throughput...                                    
 LP formation...Set parameter Username
Academic license - for non-commercial use only - expires XXXX-XX-XX
[Throughput] Optimized in: 0.11m                                        
[Throughput] Throughput:    6144.55 Gbps
[Throughput] Total accommodated flow:   30.562 %
[Throughput] NS path selection: 5.929 %
[Throughput] EW path selection: 3.848 %
[Throughput] NESW path selection:   5.325 %
[Throughput] HG path selection: 2.601 %
[Throughput] LG path selection: 7.466 %

[Coverage] Building coverage...
[Coverage] Computing coverage...
[Coverage] Out of coverage GS:  0
[Coverage] GS coverage metric:  148.79394673481124

[Stretch] Building stretch...
[Stretch] Computing stretch...                                          
[Stretch] NS stretch:   1.357
[Stretch] NS hop count: 7.0
[Stretch] EW stretch:   1.504
[Stretch] EW hop count: 8.0
[Stretch] NESW stretch: 1.253
[Stretch] NESW hop count:   6.0
[Stretch] LG stretch:   1.434
[Stretch] LG hop count: 3.5
[Stretch] HG stretch:   1.181
[Stretch] HG hop count: 11.0
Total simulation time: 2.44m
```

---


## Regenerating the Results in the Paper

Here are the steps to run the simulations and then regenerate the figures using the simulation results.

**Note**: Simulation with thousands of satellites takes time based on the capabilities of the system.


### Exploring the Search Space

To regenerate the figure. 3, 5, 6, 9, 12 execute [simulate_everything_gs_gs.py](/experiments/simulations/simulate_everything_gs_gs.py). This will simulate Starlink's first shell (by default) while individually varying all the design parameters.

```bash
python experiments/simulations/simulate_everything_gs_gs.py
```

Then execute the [exploring_search_space.ipynb](/experiments/results/plot_for_paper/exploring_search_space.ipynb) to plot the simulation results to reproduce the paper's figures.

**Note**: 
This same script can be used to regenerate the figure. 19, 20, 21, 22 of the paper by changing the values of default orbital parameters given in [shell_code_archive.py](/examples/shell_code_archive.py) or Table. 1 of the paper, [Ground station locations](/dataset/ground_stations/), and [traffic metrics](/dataset/traffic_metrics/) across them.

```python
# Starlink Shell-1 default
o = 72      # orbital planes
n = 22      # satellites per plane

i = 53      # inclination
e = 25      # angle of elevation

h = 550     # altitude


p = 50      # phase offset
t_m = 0     # time in minutes
```

```python
GS = GroundStationAtCities.TOP_100
TM = InternetTrafficAcrossCities.POP_GDP_100
```

```python
GS = GroundStationAtCities.TOP_100
TM = InternetTrafficAcrossCities.POP_GDP_100
```

```python
GS = GroundStationAtCities.TOP_1000
TM = InternetTrafficAcrossCities.POP_GDP_1000
```

```python
TM = InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
GS = GroundStationAtCities.COUNTRY_CAPITALS
```

For figure. 23, to simulate with flights, use [simulate_everything_gs_gs.py](/experiments/simulations/simulate_everything_gs_gs.py)



---

### Constellation Design Optimization

To regenerate the figure. 14, first executes all the black-box optimization [scripts](/experiments/blackbox_optimization) to find the optimized constellation design parameters for given [Ground Stations](/dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv) locations and [Traffic Matrix](/dataset/traffic_metrics/population_only_tm_Gbps_100.json) across them. Note that each script optimizes all the highlighted budgets in the Table. 1 in the paper twice (i) with the search space heuristic and (ii) without the search space heuristic, and save the `optimized parameters` and `running time` in the appropriate CSV files. 

```bash
python experiments/blackbox_optimization/variable_neighborhood_search.py
```

```bash
python experiments/blackbox_optimization/simulated_annealing.py
```

```bash
python experiments/blackbox_optimization/differential_evolution.py
```

```bash
python experiments/blackbox_optimization/adaptive_particle_swarm_optimization.py
```

Then, use [evaluate_optimized_params.py](/experiments/utilities/evaluate_optimized_params.py) to generate the network performance metrics of optimized design parameters.

First, set the corresponding CSV files path in [evaluate_optimized_params.py](/experiments/utilities/evaluate_optimized_params.py).

```python
INPUT_CSV_FILE = 'experiments/results/plot_for_paper/CSVs/blackbox_optimization/VNS/VNS_WDK.csv'
OUTPUT_CSV_FILE = 'experiments/results/plot_for_paper/CSVs/blackbox_optimization/VNS/VNS_WDK_PERF.csv'
```

Then, execute the file.

```bash
python experiments/utilities/evaluate_optimized_params.py
```

Then execute [compare_optimization_techniques.ipynb](/experiments/results/plot_for_paper/compare_optimization_techniques.ipynb) to reproduce the figures. 

---


### Exploring Mult-Shell Design


#### Comparing Single-shell vs Multi-shell Design Choices

To generate the figure. 15, first execute [single_vs_multi_shell_design.py](/experiments/multi_shell_design/single_vs_multi_shell_design.py). It will simulate all design choices and save their throughput in CSV files.

```bash
python experiments/multi_shell_design/single_vs_multi_shell_design.py
```

Then execute the second and third cells of [exploring_multi_shell_designs.ipynb](/experiments/results/plot_for_paper/exploring_multi_shell_designs.ipynb) to generate the bar charts.


#### Evaluate Inter-shell ISL Connectivity

To generate the figure. 16, first execute [variable_neighborhood_search_for_intershell_ISLs.py](/experiments/blackbox_optimization/variable_neighborhood_search_for_intershell_ISLs.py). It will optimized the design of $(i)$ single shell with +Grid ISLs, $(ii)$ two shell with +Grid inter shell ISLs, $(iii)$ three shells with inter shell ISLs for given [GSes](/dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv) and [traffic metrics](/dataset/traffic_metrics/population_only_tm_Gbps_100.json) with budget of Starlink Gen1 (S-1, S-2, S-3) in Table.1 in the paper.

```bash
python experiments/blackbox_optimization/variable_neighborhood_search_for_intershell_ISLs.py
```

Then execute [throughput_shift_inter_shell_ISL_without_handoff_h24.py](/experiments/multi_shell_design/throughput_shift_inter_shell_ISL_without_handoff_h24.py) to generate throughput metrics without handoff over $24$ hours of these three design, i.e., $(i)$ single shell with +Grid ISLs, $(ii)$ two shell with +Grid inter shell ISLs, $(iii)$ three shells with inter shell ISLs.

```bash
python experiments/multi_shell_design/throughput_shift_inter_shell_ISL_without_handoff_h24.py
```

Then execute the first cell of [exploring_multi_shell_designs.ipynb](/experiments/results/plot_for_paper/exploring_multi_shell_designs.ipynb) to reproduce the figure.


---

### Visualization of LEO Constellations

The paper also includes a handful of visuals to illustrate the nitty gritty of LEO network design, which is generated mainly by the LEOCraft 2D/3D visualization framework. To reproduce these interactive figures, execute the following scripts.

- To regenerate the figure. 1 (b) and figure. 24, execute [kuiper_shells.py](experiments/visuals_for_paper/kuiper_shells.py).

```bash
python experiments/visuals_for_paper/kuiper_shells.py
```

- To regenerate Figure. 2, execute [routes_categories.py](experiments/visuals_for_paper/routes_categories.py).

```bash
python experiments/visuals_for_paper/routes_categories.py
```


- To regenerate the figure. 1 (a), execute [coverage_cone_with_e.py](/experiments/visuals_for_paper/coverage_cone_with_e.py)

```bash
python experiments/visuals_for_paper/coverage_cone_with_e.py
```


- To regenerate the figure. 4, execute [constellation_coverage_change_with_altitude.py](/experiments/visuals_for_paper/constellation_coverage_change_with_altitude.py), open the generated HTML file.

```bash
python experiments/visuals_for_paper/constellation_coverage_change_with_altitude.py
```


- To regenerate the figure. 7 (a), execute [GS_locations.py](/experiments/visuals_for_paper/GS_locations.py), then open the generated HTML file.

```bash
python experiments/visuals_for_paper/GS_locations.py
```

- To regenerate the figure. 7 (b)-(d), execute [inclination_change_starlink.py](/experiments/visuals_for_paper/inclination_change_starlink.py).

```bash
python experiments/visuals_for_paper/inclination_change_starlink.py
```

- To regenerate Figure. 8 and Figure. 10, execute [routes_view_with_i_e.py](/experiments/visuals_for_paper/routes_view_with_i_e.py).

```bash
python experiments/visuals_for_paper/routes_view_with_i_e.py
```

- To regenerate the figure. 11, execute [topology_view_with_oxn_p.py](/experiments/visuals_for_paper/topology_view_with_oxn_p.py).

```bash
python experiments/visuals_for_paper/topology_view_with_oxn_p.py
```


- To regenerate the figure. 13, execute [HC_route_path_diversity.py](/experiments/visuals_for_paper/HC_route_path_diversity.py)

```bash
python experiments/visuals_for_paper/HC_route_path_diversity.py
```

- To regenerate Figure. 26 (a)-(b), execute [routes_view_with_h_e_raw.py](/experiments/visuals_for_paper/routes_view_with_h_e_raw.py).

```bash
python experiments/visuals_for_paper/routes_view_with_h_e_raw.py
```

- To regenerate the figure. 27, execute [satellite_ground_track.py](/experiments/visuals_for_paper/satellite_ground_track.py).

```bash
python experiments/visuals_for_paper/satellite_ground_track.py
```


- To regenerate the figure. 28, execute [ISL_usage.py](/experiments/visuals_for_paper/ISL_usage.py).

```bash
python experiments/visuals_for_paper/ISL_usage.py
```