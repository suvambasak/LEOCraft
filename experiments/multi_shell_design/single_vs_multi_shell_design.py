
'''
This script evaluates the performance of single shell design vs multi shell designs
'''

import os

import pandas as pd

from experiments.blackbox_optimization.common import \
    get_possible_oxn_arrangements
from experiments.blackbox_optimization.variable_neighborhood_search import \
    VariableNeighborhoodSearchWithDomainKnowledge
from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
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


def get_o_and_n(budget: int) -> tuple[int, int]:
    '''
    Get the number of orbits and number of satellites per orbit

    Parameters
    ----------
    budget : int
        The budget of the shell design

    Returns
    -------
    tuple[int, int]
        The number of orbits and number of satellites per orbit
    '''
    for b in range(budget, 10, -1):
        try:
            possible_combinations = get_possible_oxn_arrangements(b, 10)
            return (
                possible_combinations[-1][0],
                possible_combinations[-1][1]
            )
        except AssertionError:
            print('|- No split possible with budget:', b)


def optimize_shell_design(budget: int, altitude_km: float) -> dict[str, float | int]:
    '''
    Optimize the shell design with the given budget and altitude

    Parameters
    ----------
    budget : int
        The budget of the shell design

    altitude_km : float
        The altitude of the shell design in km

    Returns
    -------
    dict[str, float | int]
        The optimized shell design
    '''
    o, n = get_o_and_n(budget)
    bfs = VariableNeighborhoodSearchWithDomainKnowledge(
        o=o,
        n=n,
        h=altitude_km,

        e=10.0, i=30.0, p=50
    )
    bfs._heap.v.verbose = False
    # bfs.v.verbose = False
    bfs.set_max_step_size(hstep=0, istep=5, estep=5)
    return bfs.search(tolerance=3, max_iter=100)


def measure_throughput(list_of_shells: list[dict[str, float | int]]) -> float:
    '''
    Measure the throughput of the given shells design

    Parameters
    ----------
    list_of_shells : list[dict[str, float | int]]
        The shell design to measure the throughput

    Returns
    -------
    float
        The throughput of the shell design
    '''

    leo_con = LEOConstellation('LEOCON')
    leo_con.v.verbose = False
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
        )
    )

    # Adding Shells
    for idx, params in enumerate(list_of_shells):
        leo_con.add_shells(
            PlusGridShell(
                id=idx,
                orbits=params.get('o'),
                sat_per_orbit=params.get('n'),
                altitude_m=params.get('h')*1000,
                inclination_degree=params.get('i'),
                angle_of_elevation_degree=params.get('e'),
                phase_offset=params.get('p')
            )
        )

    leo_con.set_time()  # Time passed after epoch
    leo_con.set_loss_model(get_loss_model())
    leo_con.build()
    leo_con.create_network_graph()
    leo_con.generate_routes()

    # Throughput
    th = Throughput(
        leo_con,
        InternetTrafficAcrossCities.ONLY_POP_100
    )
    th.v.verbose = False
    th.build()
    th.compute()

    return th.throughput_Gbps


def evaulate_single_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Merge the budgets of all shells and use the lowest altitude
    as the altitude for the single shell design and optimize the design then record the throughput
    '''

    print('|- Evaulate single shell design....')

    shell_params = optimize_shell_design(
        sum(shell_budgets), min(shell_altitudes)
    )

    pd.DataFrame(
        [{'gbps': measure_throughput([shell_params])}]
    ).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_single_shell_design.csv'),
        index=False
    )

    print('|- Evaulate single shell design....Done.')


def evaulate_two_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Merge the budgets of either of two shells to build a bigger shell and use the lowest altitude
    as the altitude for the two shell design and optimize the design then record the throughput
    '''

    print('|- Evaulate two shell design....')

    recorded_results: list[dict[str, float | int]] = []

    # Merge the budgets of either of two shells to build a bigger shell
    for joined_shell_ids, single_shell_id in [((0, 1), 2), ((0, 2), 1), ((1, 2), 0)]:

        # Merged budgets
        joined_shell_budget = shell_budgets[
            joined_shell_ids[0]
        ] + shell_budgets[
            joined_shell_ids[1]
        ]
        joined_shell_altitude = min(
            shell_altitudes[joined_shell_ids[0]],
            shell_altitudes[joined_shell_ids[1]]
        )
        joined_shell_params = optimize_shell_design(
            joined_shell_budget, joined_shell_altitude
        )

        # Single shell budget
        single_shell_budget = shell_budgets[single_shell_id]
        single_shell_altitude = shell_altitudes[single_shell_id]
        single_shell_params = optimize_shell_design(
            single_shell_budget, single_shell_altitude
        )

        if joined_shell_budget > single_shell_budget:
            recorded_results.append({
                'gbps': measure_throughput([single_shell_params, joined_shell_params])
            })
        else:
            recorded_results.append({
                'gbps': measure_throughput([joined_shell_params, single_shell_params])
            })

    pd.DataFrame(recorded_results).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_two_shell_design.csv'),
        index=False
    )

    print('|- Evaulate two shell design....Done.')


def evaulate_three_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Optimize the design of each shell separately and then simulate
    multi shell design (with three shells) where each shells design is optimized
    '''

    print('|- Evaulate three shell design....')

    list_of_shells: list[dict[str, float | int]] = []

    # Optimize the design of each shell separately
    for budget, altitude in zip(shell_budgets, shell_altitudes):
        list_of_shells.append(optimize_shell_design(budget, altitude))

    pd.DataFrame(
        [{'gbps': measure_throughput(list_of_shells)}]
    ).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_three_shell_design.csv'),
        index=False
    )

    print('|- Evaulate three shell design....Done.')


if __name__ == "__main__":

    PREFIX_PATH = 'experiments/results/plot_for_paper/CSVs/multi_shell_design'

    STARLINK = 'STARLINK'
    TOTAL_SAT_STARLINK_SHELL_1 = 72*22
    TOTAL_SAT_STARLINK_SHELL_2 = 72*22
    TOTAL_SAT_STARLINK_SHELL_3 = 36*20
    ALTITUDE_STARLINK_SHELL_1 = 550
    ALTITUDE_STARLINK_SHELL_2 = 540
    ALTITUDE_STARLINK_SHELL_3 = 570
    STARLINK_SHELLS = [
        TOTAL_SAT_STARLINK_SHELL_1,
        TOTAL_SAT_STARLINK_SHELL_2,
        TOTAL_SAT_STARLINK_SHELL_3
    ]
    ALTITUDES_STARLINK = [
        ALTITUDE_STARLINK_SHELL_1,
        ALTITUDE_STARLINK_SHELL_2,
        ALTITUDE_STARLINK_SHELL_3
    ]

    KUIPER = 'KUIPER'
    TOTAL_SAT_KUIPER_SHELL_1 = 34*34
    TOTAL_SAT_KUIPER_SHELL_2 = 36*36
    TOTAL_SAT_KUIPER_SHELL_3 = 28*28
    ALTITUDE_KUIPER_SHELL_1 = 630
    ALTITUDE_KUIPER_SHELL_2 = 610
    ALTITUDE_KUIPER_SHELL_3 = 590
    KUIPER_SHELLS = [
        TOTAL_SAT_KUIPER_SHELL_1,
        TOTAL_SAT_KUIPER_SHELL_2,
        TOTAL_SAT_KUIPER_SHELL_3
    ]
    ALTITUDES_KUIPER = [
        ALTITUDE_KUIPER_SHELL_1,
        ALTITUDE_KUIPER_SHELL_2,
        ALTITUDE_KUIPER_SHELL_3
    ]

    evaulate_single_shell_design(KUIPER_SHELLS, ALTITUDES_KUIPER, KUIPER)
    evaulate_two_shell_design(KUIPER_SHELLS, ALTITUDES_KUIPER, KUIPER)
    evaulate_three_shell_design(KUIPER_SHELLS, ALTITUDES_KUIPER, KUIPER)

    evaulate_single_shell_design(STARLINK_SHELLS, ALTITUDES_STARLINK, STARLINK)
    evaulate_two_shell_design(STARLINK_SHELLS, ALTITUDES_STARLINK, STARLINK)
    evaulate_three_shell_design(STARLINK_SHELLS, ALTITUDES_STARLINK, STARLINK)

    # CASE-1
    # Shell 1 + Shell 2: 34x34 + 36x36
    # {'o': 129, 'n': 19, 'h': 610.0, 'i': 40.0, 'e': 17.7, 'p': 50.0, 'gbps': 5792.772632480502}
    # Shell 3: 28x28
    # {'o': 56, 'n': 14, 'h': 590.0, 'i': 32.2, 'e': 11.2, 'p': 50.0, 'gbps': 2788.381359009206}
    # Throughput: 6515.527 Gbps

    # CASE-2
    # Shell 1 + Shell 3: 34x34 + 28x28
    # {'o': 194, 'n': 10, 'h': 610.0, 'i': 43.5, 'e': 13.3, 'p': 50.0, 'gbps': 5469.2640530940225}
    # Shell 3: 36x36
    # {'o': 108, 'n': 12, 'h': 590.0, 'i': 36.0, 'e': 12.9, 'p': 50.0, 'gbps': 4111.326929392239}
    # Throughput: 6870.219 Gbps

    # CASE-3
    # Shell 2 + Shell 3: 36x36 + 28x28
    # {'o': 208, 'n': 10, 'h': 610.0, 'i': 45.3, 'e': 14.2, 'p': 50.0, 'gbps': 5719.2156963807565}
    # Shell 1: 34x34
    # {'o': 68, 'n': 17, 'h': 590.0, 'i': 38.0, 'e': 13.1, 'p': 50.0, 'gbps': 3550.915110649788}
    # Throughput: 6715.187 Gbps
