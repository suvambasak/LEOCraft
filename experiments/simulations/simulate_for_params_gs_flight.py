
'''
This script is used to simulate the LEO constellations with different parameters for flights
and generate a CSV file with the evaulation results (throughput, coverage, stretch/latency, 
hop counts, etc.) corresponds to the parameters.

The script by default runs the simulations in parallel using the LEOAviationConstellationSimulator.

At current the state the script will simulate the Starlink Shell-1 with number of orbital planes (o) 
and satellites per orbital plane (n) changes. However, one can uncomment/comment appropeate the lines 
in the script to run the simulation with other parameter or a combination of parameters:
1. Altitude
2. Angle of elevation
3. Phase offset
4. inclination
5. Time in minutes
'''


import time

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

start_time = time.perf_counter()


def get_loss_model() -> FSPL:
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


if __name__ == '__main__':

    # Output CSV file
    CSV_FILE = 'f_i_5_90.csv'

    # Parameters
    TOTAL_SAT = 72*22
    MIN_SAT_PER_ORBIT = 10

    # Starlink Shell-1 default parameters
    h = 550     # Altitude in km
    e = 25      # Angle of elevation in degree
    i = 53      # Inclination in degree

    o = 72      # Number of orbital planes
    n = 22      # Number of satellites per orbital plane
    p = 50      # Phase offset in degree

    # Time in minutes
    t_m = 0

    # All possible combinations of orbital planes and satellites per orbital plane for given budget TOTAL_SAT
    oxn = []
    for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
        if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
            oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

    # Bulk simulation setup
    # Also used to set the traffic matrics
    simulator = LEOAviationConstellationSimulator(
        InternetTrafficOnAir.ONLY_POP_100_5Mbps,
        # InternetTrafficOnAir.ONLY_POP_100_300Kbps,
        CSV_FILE
    )

    for o, n in oxn:
        # for i in range(5, 90+1, 3):
        # for h in range(500, 1001, 10):
        # for e in range(5, 50+1, 3):
        # for p in range(0, 51, 5):

        # for t_m in range(0, 24*60+1, 5):

        leo_con = LEOAviationConstellation()
        leo_con.add_ground_stations(
            GroundStation(
                GroundStationAtCities.TOP_100
            )
        )
        leo_con.add_aircrafts(Aircraft(
            FlightOnAir.FLIGHT_REPLACED_TERMINALS,
            FlightOnAir.FLIGHTS_CLUSTERS
        ))

        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())

        # Starlink Shell 1
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

    # simulator.simulate_in_serial()
    perf_log = simulator.simulate_in_parallel(max_workers=3)
    end_time = time.perf_counter()

    print()
    print(f'Total {len(perf_log)} simulation complete in {CSV_FILE}.')
    print('TOTAL TIME TAKEN: ', end_time-start_time)
