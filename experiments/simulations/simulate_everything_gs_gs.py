
'''
This script is used to simulate all parameter sweeping at once and generate 
CSV file for each paramters with the evaluation results (throughput, coverage, 
stretch/latency, hop counts, etc.).

The script by default runs the simulations in parallel using the LEOConstellationSimulator.

One can set default parameters of a LEO constellation:
1. Altitude
2. Angle of elevation
3. Phase offset
4. Number of orbital planes and satellites per orbital plane
5. Time in minutes
6. Ground Stations and Internet Traffic
    - 100 Ground Stations and corresponding Internet Traffic
        - High population TM
        - High GDP population TM
    - Country capitals Goudn Stations and corresponding Internet Traffic
        - Country capital TM

To generate the CSV files for each parameter sweep at once.
'''

import os
import time

import pandas as pd

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from LEOCraft.user_terminals.ground_station import GroundStation


def get_loss_model() -> FSPL:
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


PREFIX_PATH = 'experiments/results/plot_for_paper/CSVs/explore_search_space'


# Starlink Shell-1 default
o = 72      # orbital planes
n = 22      # satellites per plane

i = 53      # inclination
e = 25      # angle of elevation

h = 550     # altitude


p = 50      # phase offset
t_m = 0     # time in minutes


# 100 Ground Stations and corresponding Internet Traffic options
GS = GroundStationAtCities.TOP_100
TM = InternetTrafficAcrossCities.ONLY_POP_100
# TM = InternetTrafficAcrossCities.POP_GDP_100

# # Ground Stations and corresponding Internet Traffic
# TM = InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
# GS = GroundStationAtCities.COUNTRY_CAPITALS


# Simulation output files
CSV_FILE_H_24 = os.path.join(PREFIX_PATH, 'h_24.csv')

CSV_FILE_H = os.path.join(PREFIX_PATH, 'h_300_2000.csv')
CSV_FILE_E = os.path.join(PREFIX_PATH, 'e_5_50.csv')
CSV_FILE_I = os.path.join(PREFIX_PATH, 'i_5_180.csv')
CSV_FILE_OXN = os.path.join(PREFIX_PATH, 'oxn.csv')
CSV_FILE_P = os.path.join(PREFIX_PATH, 'p_0_50.csv')

CSV_FILE_HP_OXN = os.path.join(PREFIX_PATH, 'HP_oxn.csv')
CSV_FILE_HP_P = os.path.join(PREFIX_PATH, 'HP_p_0_50.csv')

CSV_FILE_OXN_VS_P = os.path.join(PREFIX_PATH, 'OXN_VS_P.csv')


TOTAL_SAT = o*n
MIN_SAT_PER_ORBIT = 10

# All possible combinations of orbital planes and satellites per orbital plane for given budget TOTAL_SAT
# While validating, if such design is possible
oxn = []
for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
    if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
        sat_per_plane = int(TOTAL_SAT/orbital_plane)

        print(f"[Validating OxN] {orbital_plane}x{sat_per_plane}...", end="")
        try:
            leo_con = LEOConstellation()
            leo_con.v.verbose = False
            leo_con.add_ground_stations(GroundStation(GS))
            leo_con.set_time(minute=t_m)
            leo_con.set_loss_model(get_loss_model())
            leo_con.add_shells(
                PlusGridShell(
                    id=0,
                    orbits=orbital_plane,
                    sat_per_orbit=sat_per_plane,
                    phase_offset=p,
                    altitude_m=1000.0*h,
                    angle_of_elevation_degree=e,
                    inclination_degree=i
                )
            )
            leo_con.build()
            leo_con.create_network_graph()

            oxn.append((orbital_plane, sat_per_plane))

            print(" Valid.")
        except Exception as exception:
            print(" Invalid.")

# ------------------------------------------------------------------
# Simulation starts here
# ------------------------------------------------------------------
_start_time = time.perf_counter()


# ------------------------------------------------------------------
# Simulation setup for 24 hours
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_H_24)
for _t_m in range(0, 24*60+1, 5):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=_t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_H_24} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for altitude h
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_H)
for _h in range(500, 2001, 10):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,
            altitude_m=1000.0*_h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_H} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for AoE e
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_E)
for _e in range(5, 50+1, 3):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=_e,
            inclination_degree=i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_E} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for inclination i
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_I)
for _i in range(5, 175, 3):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=_i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_I} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for OXN
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_OXN)
for _o, _n in oxn:
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=_o,
            sat_per_orbit=_n,
            phase_offset=p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_OXN} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_P)
for _p in range(0, 51, 5):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=_p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_P} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Getting near optimal i and e
# ------------------------------------------------------------------
df = pd.read_csv(CSV_FILE_E)
_e = df.loc[df['throughput_Gbps'].idxmax(), 'S0_e']

df = pd.read_csv(CSV_FILE_I)
_i = df.loc[df['throughput_Gbps'].idxmax(), 'S0_i']


# ------------------------------------------------------------------
# Simulation setup for OXN (HP)
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_HP_OXN)
for _o, _n in oxn:
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=_o,
            sat_per_orbit=_n,
            phase_offset=p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=_e,
            inclination_degree=_i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_HP_OXN} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P (HP)
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_HP_P)
for _p in range(0, 51, 5):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            phase_offset=_p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=_e,
            inclination_degree=_i
        )
    )
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_HP_P} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P vs OXN
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOConstellationSimulator(TM, CSV_FILE_OXN_VS_P)
for _o, _n in oxn:
    for _p in range(0, 51, 5):
        leo_con = LEOConstellation()
        leo_con.add_ground_stations(GroundStation(GS))
        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())
        leo_con.add_shells(
            PlusGridShell(
                id=0,
                orbits=_o,
                sat_per_orbit=_n,
                phase_offset=_p,
                altitude_m=1000.0*h,
                angle_of_elevation_degree=_e,
                inclination_degree=_i
            )
        )
        simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_OXN_VS_P} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


_end_time = time.perf_counter()
print('\n\n TOTAL TIME TAKEN: ', round((_end_time-_start_time)/3600, 1))

# Shell - 3
# PlusGridZigzagElevation(
#     id=0,
#     orbits=324,
#     sat_per_orbit=12,
#     altitude_pattern_m=[540000.0, 550000.0, 570000.0, 550000.0],
#     inclination_degree=44.3,
#     angle_of_elevation_degree=16.6,
#     phase_offset=50.0
# )


# # Shell - 2
# PlusGridZigzagElevation(
#     id=0,
#     orbits=324,
#     sat_per_orbit=12,
#     altitude_pattern_m=[540000.0, 550000.0],
#     inclination_degree=46.1,
#     angle_of_elevation_degree=16.2,
#     phase_offset=50.0
# )

# Shell - 1
# PlusGridShell(
#     id=0,
#     orbits=324,
#     sat_per_orbit=12,
#     altitude_m=550000.0,
#     inclination_degree=45.3,
#     angle_of_elevation_degree=16.4,
#     phase_offset=50.0
# )

# Test fluctuation with size
# PlusGridShell(
#     id=0,
#     orbits=90,
#     sat_per_orbit=10,
#     altitude_m=550000.0,
#     inclination_degree=35.1,
#     angle_of_elevation_degree=10.5,
#     phase_offset=50.0
# )
