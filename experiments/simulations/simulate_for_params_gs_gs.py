
'''
This script is used to simulate the LEO constellations with different parameters and 
generate a CSV file with the evaulation results (throughput, coverage, stretch/latency, 
hop counts, etc.) corresponds to the parameters.

The script by default runs the simulations in parallel using the LEOConstellationSimulator.

At current the state the script will simulate the Starlink Shell-1 with inclination changes 
from 5 degree to 90 degree. However, one can uncomment/comment appropeate the lines in the 
script to run the simulation with other parameter or a combination of parameters:
1. Altitude
2. Angle of elevation
3. Phase offset
4. Number of orbital planes and satellites per orbital plane
5. Time in minutes

Also, the script can be modified (uncomment/comment) to simulate with multiple shells or 
inter-shell ISL topology and other traffic metrics 
1. High population TM
2. High GDP population TM
3. Country capital TM)
'''

import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
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
    CSV_FILE = 'i_5_90.csv'

    # Parameters
    TOTAL_SAT = 324*12
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
    simulator = LEOConstellationSimulator(

        InternetTrafficAcrossCities.ONLY_POP_100,
        # InternetTrafficAcrossCities.POP_GDP_100,

        # InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP,

        CSV_FILE
    )

    # Add all constellation design to bulk simulation executor

    for i in range(5, 90+1, 3):
        # for h in range(500, 1001, 10):
        # for e in range(5, 50+1, 3):
        # for p in range(0, 51, 5):
        # for o, n in oxn:
        # for t_m in range(0, 24*60+1, 5):

        leo_con = LEOConstellation()
        leo_con.add_ground_stations(
            GroundStation(
                GroundStationAtCities.TOP_100
                # GroundStationAtCities.COUNTRY_CAPITALS
            )
        )
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
                inclination_degree=i
            )
        )

        # # To simulate with multiple shells
        # leo_con.add_shells(
        #     PlusGridShell(
        #         id=1,
        #         orbits=72,
        #         sat_per_orbit=22,
        #         altitude_m=540000.0,
        #         inclination_degree=53.2,
        #         angle_of_elevation_degree=25.0,
        #         phase_offset=50.0
        #     )
        # )
        # leo_con.add_shells(
        #     PlusGridShell(
        #         id=2,
        #         orbits=36,
        #         sat_per_orbit=20,
        #         altitude_m=570000.0,
        #         inclination_degree=70.0,
        #         angle_of_elevation_degree=25.0,
        #         phase_offset=50.0
        #     )
        # )

        # # -----------------------------------------------------------
        # # To simulate inter-shell ISL topology
        # # -----------------------------------------------------------

        # # With three shells
        # leo_con.add_shells(
        #     PlusGridZigzagElevation(
        #         id=0,
        #         orbits=324,
        #         sat_per_orbit=12,
        #         altitude_pattern_m=[540000.0, 550000.0, 570000.0, 550000.0],
        #         inclination_degree=44.3,
        #         angle_of_elevation_degree=16.6,
        #         phase_offset=50.0
        #     )
        # )

        # # With two shells
        # leo_con.add_shells(
        #     PlusGridZigzagElevation(
        #         id=0,
        #         orbits=324,
        #         sat_per_orbit=12,
        #         altitude_pattern_m=[540000.0, 550000.0],
        #         inclination_degree=46.1,
        #         angle_of_elevation_degree=16.2,
        #         phase_offset=50.0
        #     )
        # )

        # # -----------------------------------------------------------

        simulator.add_constellation(leo_con)

    # simulator.simulate_in_serial()
    perf_log = simulator.simulate_in_parallel(max_workers=3)

    end_time = time.perf_counter()

    print()
    print(f'Total {len(perf_log)} simulation complete in {CSV_FILE}.')
    print('TOTAL TIME TAKEN: ', end_time-start_time)
