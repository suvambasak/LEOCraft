
'''
This script simulates LEO constellation with inter-satellite links (ISLs) 
between two and three shells for 24 hours. Records the throughput changes
due to the topological shift in plus grid connectivity.
'''

import os

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


def simulate_h24(params):
    'Record the throughput for 24 hours'

    def get_loss_model() -> FSPL:
        loss_model = FSPL(
            28.5*1000000000,    # Frequency in Hz
            98.4,               # Tx power dBm
            0.5*1000000000,     # Bandwidth Hz
            13.6                # G/T ratio
        )
        loss_model.set_Tx_antenna_gain(gain_dB=34.5)
        return loss_model

    # Simulate the constellation for 24 hours
    # with a time step of 5 minutes
    simulator = LEOConstellationSimulator(
        InternetTrafficAcrossCities.ONLY_POP_100,
        os.path.join(PREFIX_PATH, f'{params.topology_type}_h_24')
    )
    for t_m in range(0, 24*60+1, 5):

        leo_con = LEOConstellation()
        leo_con.add_ground_stations(
            GroundStation(
                GroundStationAtCities.TOP_100
            )
        )
        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())

        # Add the shells based on the topology type
        if params.topology_type == 'SS_ISL':
            shell = PlusGridShell(
                id=0,
                orbits=params.S0_o,
                sat_per_orbit=params.S0_n,
                phase_offset=params.S0_p,
                altitude_m=params.S0_h_km*1000,
                angle_of_elevation_degree=params.S0_e,
                inclination_degree=params.S0_i
            )
        elif params.topology_type == 'IS2_ISL':
            shell = PlusGridZigzagElevation(
                id=0,
                orbits=params.S0_o,
                sat_per_orbit=params.S0_n,
                altitude_pattern_m=[540000.0, 550000.0],
                inclination_degree=params.S0_i,
                angle_of_elevation_degree=params.S0_e,
                phase_offset=params.S0_p
            )
        elif params.topology_type == 'IS3_ISL':
            shell = PlusGridZigzagElevation(
                id=0,
                orbits=params.S0_o,
                sat_per_orbit=params.S0_n,
                altitude_pattern_m=[
                    540000.0, 550000.0, 570000.0, 550000.0
                ],
                inclination_degree=params.S0_i,
                angle_of_elevation_degree=params.S0_e,
                phase_offset=params.S0_p
            )

        leo_con.add_shells(shell)
        simulator.add_constellation(leo_con)

    simulator.simulate_in_parallel(max_workers=3)


if __name__ == "__main__":

    PREFIX_PATH = 'experiments/results/plot_for_paper/CSVs/multi_shell_design'

    for params in pd.read_csv(
        os.path.join(
            PREFIX_PATH, 'optimized_designs_DK.csv'
        )
    ).itertuples(
        index=True, name='Params'
    ):
        simulate_h24(params)
        print('Simulation completed for:', params.topology_type)
