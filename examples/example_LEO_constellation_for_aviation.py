'''
This example demonstrates how to create a LEO constellation for aviation
using the LEOCraft. 

It includes the following steps:
1. Import necessary modules and classes.
2. Define the path loss model using FSPL (Free Space Path Loss).
3. Create an instance of the LEOAviationConstellation class.
4. Add ground stations and aircrafts to the constellation.
5. Define the satellite shells using PlusGridShell.
6. Set the time and loss model for the constellation.
7. Build the constellation and create the network graph.
8. Generate routes for the aircrafts.
9. Compute throughput, coverage, and latency/stretch metrics.
10. Export the simulation datasets to a specified output path.
'''

import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.dataset import (FlightOnAir, GroundStationAtCities,
                              InternetTrafficOnAir)
from LEOCraft.performance.aviation.coverage import Coverage
from LEOCraft.performance.aviation.stretch import Stretch
from LEOCraft.performance.aviation.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.aircraft import Aircraft
from LEOCraft.user_terminals.ground_station import GroundStation


# Exporting all simulation datasets
OUTPUT_PATH = './Starlink'

start_time = time.perf_counter()


# Pathloss model
loss_model = FSPL(
    28.5*1000000000,    # Frequency in Hz
    98.4,               # Tx power dBm
    0.5*1000000000,     # Bandwidth Hz
    13.6                # G/T ratio
)
loss_model.set_Tx_antenna_gain(gain_dB=34.5)


leo_con = LEOAviationConstellation('Starlink-aviation')
leo_con.v.verbose = True

# Adding Ground Stations and Aircrafts
leo_con.add_ground_stations(
    GroundStation(
        GroundStationAtCities.TOP_100
        # GroundStationAtCities.TOP_1000
    )
)
leo_con.add_aircrafts(
    Aircraft(
        replaced_gs_csv=FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        flight_cluster_csv=FlightOnAir.FLIGHTS_CLUSTERS
    )
)


# Adding Shells

# Starlink Shell 1
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
# Starlink Shell 2
leo_con.add_shells(
    PlusGridShell(
        id=1,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=540000.0,
        inclination_degree=53.2,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)
# Starlink Shell 3
leo_con.add_shells(
    PlusGridShell(
        id=2,
        orbits=36,
        sat_per_orbit=20,
        altitude_m=570000.0,
        inclination_degree=70.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)


leo_con.set_time()  # Time passed after epoch
leo_con.set_loss_model(loss_model)
leo_con.build()
leo_con.create_network_graph()

leo_con.generate_routes()


# Throughput
th = Throughput(
    leo_con,
    # InternetTrafficOnAir.ONLY_POP_100_300Kbps
    InternetTrafficOnAir.ONLY_POP_100_5Mbps
)
th.build()
th.compute()


# Coverage
cov = Coverage(leo_con)
cov.build()
cov.compute()


# Latency/Stretch
sth = Stretch(leo_con)
sth.build()
sth.compute()
end_time = time.perf_counter()


# Constellation
leo_con.export_gsls(OUTPUT_PATH)
leo_con.export_fsls(OUTPUT_PATH)
leo_con.export_routes(OUTPUT_PATH)
leo_con.export_no_path_found(OUTPUT_PATH)
leo_con.export_k_path_not_found(OUTPUT_PATH)

# Shells
for shell in leo_con.shells:
    shell.export_satellites(OUTPUT_PATH)
    shell.export_isls(OUTPUT_PATH)

# Ground stations
leo_con.ground_stations.export(OUTPUT_PATH)
# Flight terminals
leo_con.aircrafts.export(OUTPUT_PATH)

# Throughputs
th.export_path_selection(OUTPUT_PATH)
th.export_LP_model(OUTPUT_PATH)

# Stretch
sth.export_stretch_dataset(OUTPUT_PATH)


print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
