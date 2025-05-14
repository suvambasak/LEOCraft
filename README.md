# LEOCraft - A Flow Level LEO Network Simulator

A modular and extensible LEO network simulation platform to explore traffic flow, throughput, stretch/latency, and coverage. LEOCraft operate as flow level to evaulate given LEO constellation quickly.


# Table of Contents
- [Getting Started](#Getting-started)
    - [Setup the Simulation Environment](#setup-the-simulation-environment)
    - [Get the Academic License for Gurobi Optimizer](#get-the-academic-license-for-gurobi-optimizer)
    - [Test the Simulation Environment](#test-the-simulation-environment)
    - [Simulate with LEOCraft](#simulate-with-leocraft)
        - [Create LEO Constellation](#create-leo-constellation)
        - [Measure Throughput](#measure-throughput)
        - [Measure Stretch/Latency](#measure-stretchlatency)
        - [Measure Coverage](#measure-coverage)
    - [Visualize with LEOCraft](#visualize-with-leocraft)
        - [Visualize in 2D](#visualize-in-2d)
        - [Visualize in 3D](#visualize-in-3d)
    - [Examples](#examples)
- [Extend LEOCraft](#extend-leocraft)
- [License](#license)
- [Cite This Work](#cite-this-work)
- [Artifact Evaluation](#artifact-evaluation)
- [Credits](#credits)

# Getting Started

## Setup the Simulation Environment

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


## Get the Academic License for Gurobi Optimizer

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


## Test the Simulation Environment

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

## Simulate with LEOCraft

### Create LEO Constellation

```python
from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
```


```python
loss_model = FSPL(
    28.5*1000000000,    # Frequency in Hz
    98.4,               # Tx power dBm
    0.5*1000000000,     # Bandwidth Hz
    13.6                # G/T ratio
)
loss_model.set_Tx_antenna_gain(gain_dB=34.5)
```

```python
leo_con = LEOConstellation('Starlink')
leo_con.add_ground_stations(
    GroundStation(
        GroundStationAtCities.TOP_100
    )
)

leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=550000.0,
        inclination_degree=53.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)

leo_con.set_time(second=3)  # Time passed after epoch
leo_con.set_loss_model(loss_model)
leo_con.build()
leo_con.create_network_graph()

leo_con.generate_routes()
```

```bash
[LEOConstellation] Building ground stations...
[LEOConstellation] Building shells...
[LEOConstellation] Building ground to satellite links...                
[LEOConstellation] GSLs generated in: 0.11m                             
[LEOConstellation] Adding satellites into network graph...
[LEOConstellation] Adding ISLs into network graph...
[LEOConstellation] Routes generated in: 2.83m 
```

### Measure Throughput

```python
from LEOCraft.dataset import InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
```

```python
th = Throughput(
    leo_con,
    InternetTrafficAcrossCities.ONLY_POP_100
)
th.build()
th.compute()
```

```bash
[Throughput] Building throughput...
[Throughput] Computing throughput...                                    
 LP formation...Set parameter Username
Set parameter LicenseID to value XXXXXXX
Academic license - for non-commercial use only - expires 20XX-XX-XX
[Throughput] Optimized in: 0.02m                                        
[Throughput] Throughput:        2820.032 Gbps
[Throughput] Total accommodated flow:   15.209 %
[Throughput] NS path selection: 1.77 %
[Throughput] EW path selection: 1.455 %
[Throughput] NESW path selection:       1.916 %
[Throughput] HG path selection: 0.999 %
[Throughput] LG path selection: 6.945 %
```

### Measure Stretch/Latency

```python
from LEOCraft.performance.basic.stretch import Stretch
```

```python
sth = Stretch(leo_con)
sth.build()
sth.compute()
```

```bash
[Stretch] Building stretch...
[Stretch] Computing stretch...                                          
[Stretch] NS stretch:   1.868
[Stretch] NS hop count: 8.0
[Stretch] EW stretch:   1.668
[Stretch] EW hop count: 8.0
[Stretch] NESW stretch: 1.285
[Stretch] NESW hop count:       6.0
[Stretch] LG stretch:   1.479
[Stretch] LG hop count: 4.0
[Stretch] HG stretch:   1.263
[Stretch] HG hop count: 12.0
```

### Measure Coverage

```python
from LEOCraft.performance.basic.stretch import Stretch
```

```python
cov = Coverage(leo_con)
cov.build()
cov.compute()
```

```bash
[Coverage] Building coverage...
[Coverage] Computing coverage...
[Coverage] Out of coverage GS:  0
[Coverage] GS coverage metric:  111.9799753395037
```





## Visualize with LEOCraft

### Visualize in 2D

```python
from LEOCraft.visuals.sat_view_2D import SatView2D

view = SatView2D(leo_con, default_zoom=2.0)

view.add_all_satellites()
view.add_coverages('S0-0', 'S0-1', 'S0-40', 'S0-31', 'S0-30')
view.add_routes('G-0_G-1', 'G-1_G-2', 'G-2_G-3', 'G-30_G-33', k=1)

view.build()

view.export_html('docs/html/Starlink_2D.html')
```

```bash
[SatView2D] Building view 2D...  
[SatView2D] Exporting HTML...  
```

The interactive 2D visualization [Starlink_2D.html](/docs/html/Starlink_2D.html).

<p align="center">
<img height="400px" src="docs/images/Starlink_2D.png">
</p>

### Visualize in 3D

```python
from LEOCraft.visuals.sat_view_3D import SatView3D

view = SatView3D(leo_con)

view.add_all_satellites()
view.add_routes('G-0_G-1', 'G-1_G-2', 'G-2_G-3', 'G-30_G-33', k=1)

view.build()

view.export_html('docs/html/Starlink_3D.html')
```

```bash
[SatView3D] Building raw view 3D...  
[SatView3D] Exporting HTML...  
```


The interactive 2D visualization [Starlink_3D.html](/docs/html/Starlink_3D.html).

<p align="center">
<img height="400px" src="docs/images/Starlink_3D.png">
</p>

## Examples

# Extend LEOCraft

# License
This work is licensed under the [MIT License](/LICENSE).


# Cite This Work

## Plain text

```

```

## BibTeX

```bibtex

```

# Artifact Evaluation
For executing the experiments and regenerating the figures in the paper a staright forward steps are given in [ARTIFACT_EVALUATION](/ARTIFACT_EVALUATION.md).


# Credits

Contributors whose support and expertise have been invaluable in the development of **LEOCraft**:

- [**Amitangshu Pal**](https://www.cse.iitk.ac.in/users/amitangshu/)
- [**Debopam Bhattacherjee**](https://bdebopam.github.io)
