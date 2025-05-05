# Artifact Evaluation

## Getting Started

### Setup Conda Environment

Clone the LEOCraft repository.

```bash
git clone https://github.com/suvambasak/LEOCraft.git
```

```bash
cd LEOCraft
```

Create conda environment from [environment.yml](/tools/environment.yml) or[ environment_macOS.yml](/tools/environment_macOS.yml).

```bash
conda env create -f tools/environment.yml
```
or

```bash
conda env create -f tools/environment_macOS.yml
```

Activate `leocraft` environment

```bash
conda activate leocraft
```

---




### Get the Academic License for Gurobi Optimizer

LEOCraft uses [Gurobi Optimizer](https://www.gurobi.com/) to solve throughput maximization linear program.

- Extract the license tools [licensetools12.0.1_linux64.tar.gz](/tools/licensetools12.0.1_linux64.tar.gz) or download the the [license tools](https://support.gurobi.com/hc/en-us/articles/360059842732-How-do-I-set-up-a-license-without-installing-the-full-Gurobi-package) based on your platform.

- [Sign up](https://portal.gurobi.com/iam/login/) and generate free [Named-User Academic](https://portal.gurobi.com/iam/licenses/request) license.

- Install the license.

```bash
cd licensetools12.0.1_linux64/
```

```bash
./grbgetkey <LICENSE_KEY>
```

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

Hit enter and store the `gurobi.lic` file.

---

### Test the Environment

Export `LEOCraft` path in the shell. This will allow seamless execution of scripts.


```bash
export PYTHONPATH=$(pwd)
```

Or for instance, if the repository is cloned at `/mnt/Storage/Projects/LEOCraft`

```bash
export PYTHONPATH="/mnt/Storage/Projects/LEOCraft"
```

Now execute the script: [example_starlink.py](/examples/example_starlink.py) to simulate starlink multi shell LEO constellatiion.

```bash
python examples/example_starlink.py
```

If you see something like this then `LEOCraft` setup is successfull.

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
[Throughput] Throughput:	6144.55 Gbps
[Throughput] Total accommodated flow:	30.562 %
[Throughput] NS path selection:	5.929 %
[Throughput] EW path selection:	3.848 %
[Throughput] NESW path selection:	5.325 %
[Throughput] HG path selection:	2.601 %
[Throughput] LG path selection:	7.466 %

[Coverage] Building coverage...
[Coverage] Computing coverage...
[Coverage] Out of coverage GS:	0
[Coverage] GS coverage metric:	148.79394673481124

[Stretch] Building stretch...
[Stretch] Computing stretch...                                          
[Stretch] NS stretch:	1.357
[Stretch] NS hop count:	7.0
[Stretch] EW stretch:	1.504
[Stretch] EW hop count:	8.0
[Stretch] NESW stretch:	1.253
[Stretch] NESW hop count:	6.0
[Stretch] LG stretch:	1.434
[Stretch] LG hop count:	3.5
[Stretch] HG stretch:	1.181
[Stretch] HG hop count:	11.0
Total simulation time: 2.44m
```

---


## Regenerating the Figures in the Paper

Here is the steps to run the simulations and then regenerate the figures using the simulation results.


### Orbital Parameters Sweep

To regenerate the Figure. 3, 5, 6, 9, 12 execute the script [simulate_everything_gs_gs.py](/experiments/simulations/simulate_everything_gs_gs.py)

```bash
python experiments/simulations/simulate_everything_gs_gs.py
```

Then execute the [exploring_search_space](/experiments/results/plot_for_paper/exploring_search_space.ipynb) notebook.


---

### Constellation Design Optimization

To regenerate the Figure. 14, first executes all the black-box optimization [scripts](/experiments/blackbox_optimization) to find the optimized constellation design parameters for given [Ground Stations](/dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv) locations and [Traffic Matrix](/dataset/traffic_metrics/population_only_tm_Gbps_100.json) across them.

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

Now use script [evaluate_optimized_params.py](/experiments/utilities/evaluate_optimized_params.py) to generate the performance metrics of optimized design parameters.

Set the corresponding CSV files path.

```python
INPUT_CSV_FILE = 'experiments/results/plot_for_paper/CSVs/blackbox_optimization/VNS/VNS_WDK.csv'
OUTPUT_CSV_FILE = 'experiments/results/plot_for_paper/CSVs/blackbox_optimization/VNS/VNS_WDK_PERF.csv'
```

Execute the scripts

```bash
python experiments/utilities/evaluate_optimized_params.py
```

Then execute notebook [compare_optimization_techniques.ipynb](/experiments/results/plot_for_paper/compare_optimization_techniques.ipynb) notebook. 

---


### Exploring Mult-Shell Designs

To generate the Figure. 15, first execute the script [single_vs_multi_shell_design.py](/experiments/multi_shell_design/single_vs_multi_shell_design.py).

```bash
python experiments/multi_shell_design/single_vs_multi_shell_design.py
```

Then execute the second and third cells of notebook [exploring_multi_shell_designs.ipynb](/experiments/results/plot_for_paper/exploring_multi_shell_designs.ipynb) to genrate the bar charts.

To generate the Figure. 16, first execute the script [variable_neighborhood_search_for_intershell_ISLs.py](/experiments/blackbox_optimization/variable_neighborhood_search_for_intershell_ISLs.py).

```bash
python experiments/blackbox_optimization/variable_neighborhood_search_for_intershell_ISLs.py
```

Then execute the script [throughput_shift_inter_shell_ISL_without_handoff_h24.py](/experiments/multi_shell_design/throughput_shift_inter_shell_ISL_without_handoff_h24.py).

```bash
python experiments/multi_shell_design/throughput_shift_inter_shell_ISL_without_handoff_h24.py
```

Then execute the first cell of [exploring_multi_shell_designs.ipynb](/experiments/results/plot_for_paper/exploring_multi_shell_designs.ipynb) to genrate the plot.


---

### Visualization of LEO Constellations


- To regenerate Figure. 1 (b) and Figure. 24, execute script [kuiper_shells.py](experiments/visuals_for_paper/kuiper_shells.py).

```bash
python experiments/visuals_for_paper/kuiper_shells.py
```

- To regenerate Figure. 2, execute script [routes_categories.py](experiments/visuals_for_paper/routes_categories.py).

```bash
python experiments/visuals_for_paper/routes_categories.py
```


- To regenerate Figure. 1 (a), execute script [coverage_cone_with_e.py](/experiments/visuals_for_paper/coverage_cone_with_e.py)

```bash
python experiments/visuals_for_paper/coverage_cone_with_e.py
```


- To regenerate Figure. 4, execute script [constellation_coverage_change_with_altitude.py](/experiments/visuals_for_paper/constellation_coverage_change_with_altitude.py), open the generated HTML file.

```bash
python experiments/visuals_for_paper/constellation_coverage_change_with_altitude.py
```


- To regenerate Figure. 7 (a), execute script [GS_locations.py](/experiments/visuals_for_paper/GS_locations.py), then open the generated HTML file.

```bash
python experiments/visuals_for_paper/GS_locations.py
```



- To regenerate Figure. 7 (b)-(d), execute script: [inclination_change_starlink.py](/experiments/visuals_for_paper/inclination_change_starlink.py).

```bash
python experiments/visuals_for_paper/inclination_change_starlink.py
```

- To regenerate Figure. 8 and Figure. 10, execute [routes_view_with_i_e.py](/experiments/visuals_for_paper/routes_view_with_i_e.py).

```bash
python experiments/visuals_for_paper/routes_view_with_i_e.py
```

- To regenerate Figure. 11, execute script [topology_view_with_oxn_p.py](/experiments/visuals_for_paper/topology_view_with_oxn_p.py).

```bash
python experiments/visuals_for_paper/topology_view_with_oxn_p.py
```


- To regenerate Figure. 13, execute script [HC_route_path_diversity.py](/experiments/visuals_for_paper/HC_route_path_diversity.py)

```bash
python experiments/visuals_for_paper/HC_route_path_diversity.py
```

- To regenerate Figure. 26 (a)-(b), execute script [routes_view_with_h_e_raw.py](/experiments/visuals_for_paper/routes_view_with_h_e_raw.py).

```bash
python experiments/visuals_for_paper/routes_view_with_h_e_raw.py
```

- To regenerate Figure. 27, execute script [satellite_ground_track.py](/experiments/visuals_for_paper/satellite_ground_track.py).

```bash
python experiments/visuals_for_paper/satellite_ground_track.py
```


- To regenerate Figure. 28, execute script [ISL_usage.py](/experiments/visuals_for_paper/ISL_usage.py).

```bash
python experiments/visuals_for_paper/ISL_usage.py
```


---