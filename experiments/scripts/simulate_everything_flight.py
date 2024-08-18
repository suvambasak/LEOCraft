import time

import pandas as pd

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.dataset import (FlightOnAir, GroundStationAtCities,
                              InternetTrafficOnAir)
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.simulator.LEO_aviation_constellation_simulator import \
    LEOAviationConstellationSimulator
from LEOCraft.user_terminals.aircraft import Aircraft
from LEOCraft.user_terminals.ground_station import GroundStation


TM = InternetTrafficOnAir.ONLY_POP_100_300Kbps
GS = GroundStationAtCities.TOP_100

# Starlink Shell-3
o = 36
n = 20

i = 70
e = 25

h = 570


p = 50
t_m = 0


def get_loss_model() -> FSPL:
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


# OUTOUR FILEs
CSV_FILE_H_24 = 'h_24.csv'

CSV_FILE_H = 'h_300_2000.csv'
CSV_FILE_E = 'e_5_50.csv'
CSV_FILE_I = 'i_5_90.csv'
CSV_FILE_OXN = 'oxn.csv'
CSV_FILE_P = 'p_0_50.csv'

CSV_FILE_HP_OXN = 'HP_oxn.csv'
CSV_FILE_HP_P = 'HP_p_0_50.csv'

CSV_FILE_OXN_VS_P = 'OXN_VS_P.csv'


# Constellation defaults
TOTAL_SAT = o*n
MIN_SAT_PER_ORBIT = 10

oxn = []
for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
    if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
        oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

# ------------------------------------------------------------------
# Simulation starts here
# ------------------------------------------------------------------
_start_time = time.perf_counter()


# ------------------------------------------------------------------
# Simulation setup for 24 hours
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_H_24)
for _t_m in range(0, 24*60+1, 5):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=_t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=e,
        inclination_degree=i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_H_24} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for altitude h
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_H)
for _h in range(500, 1001, 10):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=p,
        altitude_m=1000.0*_h,
        angle_of_elevation_degree=e,
        inclination_degree=i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_H} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for AoE e
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_E)
for _e in range(5, 50+1, 3):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=_e,
        inclination_degree=i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_E} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for inclination i
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_I)
for _i in range(5, 90+1, 3):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=e,
        inclination_degree=_i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_I} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for OXN
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_OXN)
for _o, _n in oxn:
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=_o,
        sat_per_orbit=_n,
        phase_offset=p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=e,
        inclination_degree=i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_OXN} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_P)
for _p in range(0, 51, 5):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=_p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=e,
        inclination_degree=i
    ))
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
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_HP_OXN)
for _o, _n in oxn:
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=_o,
        sat_per_orbit=_n,
        phase_offset=p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=_e,
        inclination_degree=_i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_HP_OXN} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P (HP)
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_HP_P)
for _p in range(0, 51, 5):
    leo_con = LEOAviationConstellation()
    leo_con.add_ground_stations(GroundStation(GS))
    leo_con.add_aircrafts(Aircraft(
        FlightOnAir.FLIGHT_REPLACED_TERMINALS,
        FlightOnAir.FLIGHTS_CLUSTERS
    ))
    leo_con.set_time(minute=t_m)
    leo_con.set_loss_model(get_loss_model())
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=o,
        sat_per_orbit=n,
        phase_offset=_p,
        altitude_m=1000.0*h,
        angle_of_elevation_degree=_e,
        inclination_degree=_i
    ))
    simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_HP_P} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


# ------------------------------------------------------------------
# Simulation setup for phase offset P vs OXN
# ------------------------------------------------------------------
start_time = time.perf_counter()
simulator = LEOAviationConstellationSimulator(TM, CSV_FILE_OXN_VS_P)
for _o, _n in oxn:
    for _p in range(0, 51, 5):
        leo_con = LEOAviationConstellation()
        leo_con.add_ground_stations(GroundStation(GS))
        leo_con.add_aircrafts(Aircraft(
            FlightOnAir.FLIGHT_REPLACED_TERMINALS,
            FlightOnAir.FLIGHTS_CLUSTERS
        ))
        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())
        leo_con.add_shells(PlusGridShell(
            id=0,
            orbits=_o,
            sat_per_orbit=_n,
            phase_offset=_p,
            altitude_m=1000.0*h,
            angle_of_elevation_degree=_e,
            inclination_degree=_i
        ))
        simulator.add_constellation(leo_con)
perf_log = simulator.simulate_in_parallel(max_workers=3)
end_time = time.perf_counter()

print(f'{CSV_FILE_OXN_VS_P} with {len(perf_log)} Complete.')
print('\n\n TOTAL TIME TAKEN: ', round((end_time-start_time)/3600, 1))


_end_time = time.perf_counter()
print('\n\n TOTAL TIME TAKEN: ', round((_end_time-_start_time)/3600, 1))
