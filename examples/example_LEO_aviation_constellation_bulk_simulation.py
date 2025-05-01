'''
This example demonstrates how to use the LEOAviationConstellationSimulator
to simulate a LEO constellation for aviation applications in bulk.

It includes the following steps:
- Define the loss model using FSPL (Free Space Path Loss).
- Initialize the LEOAviationConstellationSimulator with the desired traffic model 
  and CSV file for logging performance evaulation dataset.
- Loop through the combinations of parameters and create a LEOAviationConstellation
  object for each combination.
- Add ground stations, aircrafts, set the time, and loss model for the constellation.
- Add shells to the constellation, for this instance the Starlink Shell-1 parameters.
  Optionally, add more shells for a multi-shell LEO constellation.
- Run the simulation in parallel for all combinations of parameters.
  This example is designed to be run in parallel to speed up the simulation process.
  It is important to note that the simulation may take a significant amount of time
  to complete, depending on the number of combinations and the complexity of the
  constellation.
'''

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

    # Parameters
    CSV_FILE = 'performance_log.csv'
    TOTAL_SAT = 72*22
    MIN_SAT_PER_ORBIT = 10

    # Starlink Shell-1
    h = 550
    e = 25
    i = 53

    o = 72
    n = 22
    p = 50

    # Time in minutes
    t_m = 0

    # All possible combinations of orbital planes and satellites per orbital plane for given budget TOTAL_SAT
    oxn = []
    for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
        if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
            oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

    # Simulation to be run in parallel
    # Add a bulk of simulations for different parameters (i.e., parameters sweeping)

    simulator = LEOAviationConstellationSimulator(
        InternetTrafficOnAir.ONLY_POP_100_5Mbps,
        CSV_FILE
    )

    # for t_m in range(0, 24*60+1, 5):
    # for h in range(300, 2000, 10):
    # for e in range(5, 85+1, 3):
    # for i in range(5, 175+1, 3):
    # for p in range(0, 51, 5):
    for o, n in oxn:

        leo_con = LEOAviationConstellation()
        leo_con.add_ground_stations(
            GroundStation(GroundStationAtCities.TOP_100)
        )
        leo_con.add_aircrafts(Aircraft(
            FlightOnAir.FLIGHT_REPLACED_TERMINALS,
            FlightOnAir.FLIGHTS_CLUSTERS
        ))

        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())

        # Starlink Shell 1
        leo_con.add_shells(PlusGridShell(
            id=0,

            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,

            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        ))

        # Could add more shells for multi shell LEO constellation

        # leo_con.add_shells(PlusGridShell(
        #     id=1,
        #     orbits=72,
        #     sat_per_orbit=22,
        #     altitude_m=540000.0,
        #     inclination_degree=53.2,
        #     angle_of_elevation_degree=25.0,
        #     phase_offset=p
        # ))
        # leo_con.add_shells(PlusGridShell(
        #     id=2,
        #     orbits=36,
        #     sat_per_orbit=20,
        #     altitude_m=570000.0,
        #     inclination_degree=70.0,
        #     angle_of_elevation_degree=25.0,
        #     phase_offset=p
        # ))

        simulator.add_constellation(leo_con)

    # simulator.simulate_in_serial()
    simulator.simulate_in_parallel(max_workers=3)

    print(f'{CSV_FILE}\tComplete.')
