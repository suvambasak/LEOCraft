
'''
This script evaluates the performance of single shell design vs multi shell design
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


def evaulate_single_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Merge the budgets of all shells and use the lowest altitude
    as the altitude for the single shell design and optimize the design then record the throughput
    '''
    try:
        o, n = get_possible_oxn_arrangements(sum(shell_budgets), 10)[-1]
    except AssertionError:
        o, n = get_possible_oxn_arrangements(sum(shell_budgets)//10*10, 10)[-1]

    recorded_results: list[dict[str, float | int]] = []

    bfs = VariableNeighborhoodSearchWithDomainKnowledge(
        e=10.0,
        h=shell_altitudes[0],
        i=30.0,

        n=n,
        o=o,
        p=50
    )
    bfs.set_h_bound(shell_altitudes[0]+5, shell_altitudes[0]-5)
    bfs.set_max_step_size(hstep=5, istep=5, estep=5)
    recorded_results.append(bfs.search(tolerance=3, max_iter=100))

    print('________________Single Shell Design Results_________________')
    print(
        f"Budget: {o*n} at Altitude: {shell_altitudes[0]} through {recorded_results[0]['gbps']}"
    )
    print('____________________________________________________________')

    pd.DataFrame(recorded_results).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_single_shell_design.csv'),
        index=False
    )


def evaulate_two_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Merge the budgets of either of two shells to build a bigger shell and use the lowest altitude
    as the altitude for the two shell design and optimize the design then record the throughput
    '''

    record_throughput: list[dict[str, float]] = []

    def setup_budget(budget) -> tuple[int, int]:
        try:
            o, n = get_possible_oxn_arrangements(budget, 10)[-1]
        except AssertionError:
            o, n = get_possible_oxn_arrangements(budget//10*10, 10)[-1]
        return o, n

    for shell_a, shell_b in [((0, 1), 2), ((1, 2), 0), ((0, 2), 1)]:

        # Optimized shell a with the budget of two shells (merged)
        o_of_shell_a, n_of_shell_a = setup_budget(
            shell_budgets[shell_a[0]]+shell_budgets[shell_a[1]]
        )
        bfs = VariableNeighborhoodSearchWithDomainKnowledge(
            e=10.0,
            h=min(shell_altitudes[shell_a[0]], shell_altitudes[shell_a[1]]),
            i=30.0,

            n=o_of_shell_a,
            o=n_of_shell_a,
            p=50
        )
        bfs.set_h_bound(
            min(shell_altitudes[shell_a[0]], shell_altitudes[shell_a[1]])+5,
            min(shell_altitudes[shell_a[0]], shell_altitudes[shell_a[1]])-5
        )
        bfs.set_max_step_size(hstep=5, istep=5, estep=5)
        result_shell_a = bfs.search(tolerance=3, max_iter=100)

        # Optimized shell b with the budget of one shell
        o_of_shell_b, n_of_shell_b = setup_budget(shell_budgets[shell_b])
        bfs = VariableNeighborhoodSearchWithDomainKnowledge(
            e=10.0,
            h=shell_altitudes[shell_b],
            i=30.0,

            n=n_of_shell_b,
            o=o_of_shell_b,
            p=50
        )
        bfs.set_h_bound(
            shell_altitudes[shell_b]+5,
            shell_altitudes[shell_b]-5
        )
        bfs.set_max_step_size(hstep=5, istep=5, estep=5)
        result_shell_b = bfs.search(tolerance=3, max_iter=100)

        # Simulate multi shell design (with two shells) where each shells design is optimized
        leo_con = LEOConstellation('LEOCON')
        leo_con.v.verbose = True
        leo_con.add_ground_stations(
            GroundStation(
                GroundStationAtCities.TOP_100
            )
        )
        # Adding Shells
        for idx, results in enumerate([result_shell_a, result_shell_b]):
            leo_con.add_shells(
                PlusGridShell(
                    id=idx,
                    orbits=results.get('o'),
                    sat_per_orbit=results.get('n'),
                    altitude_m=results.get('h')*1000,
                    inclination_degree=results.get('i'),
                    angle_of_elevation_degree=results.get('e'),
                    phase_offset=results.get('p')
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
        th.build()
        th.compute()

        print('________________Two Shell Design Results_________________')
        print(f"Throughput {th.throughput_Gbps} Gbps")
        print('____________________________________________________________')
        record_throughput.append({'gbps': th.throughput_Gbps})

    pd.DataFrame(record_throughput).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_two_shell_design.csv'),
        index=False
    )


def evaulate_three_shell_design(
    shell_budgets: list[int],
    shell_altitudes: list[float],
    prefix: str
):
    '''
    Optimize the design of each shell separately and then simulate
    multi shell design (with three shells) where each shells design is optimized
    '''

    recorded_results: list[dict[str, float | int]] = []

    # Optimize the design of each shell separately
    for budget, altitude in zip(shell_budgets, shell_altitudes):

        try:
            o, n = get_possible_oxn_arrangements(budget, 10)[-1]
        except AssertionError:
            o, n = get_possible_oxn_arrangements(budget//10*10, 10)[-1]

        bfs = VariableNeighborhoodSearchWithDomainKnowledge(
            e=10.0,
            h=altitude,
            i=30.0,

            n=n,
            o=o,
            p=50
        )
        bfs.set_h_bound(altitude+5, altitude-5)
        bfs.set_max_step_size(hstep=5, istep=5, estep=5)
        result = bfs.search(tolerance=3, max_iter=100)
        recorded_results.append(result)

    # Simulate multi shell design (with three shells) where each shells design is optimized
    leo_con = LEOConstellation('LEOCON')
    leo_con.v.verbose = True
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
        )
    )

    # Adding Shells
    for idx, results in enumerate(recorded_results):
        leo_con.add_shells(
            PlusGridShell(
                id=idx,
                orbits=results.get('o'),
                sat_per_orbit=results.get('n'),
                altitude_m=results.get('h')*1000,
                inclination_degree=results.get('i'),
                angle_of_elevation_degree=results.get('e'),
                phase_offset=results.get('p')
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
    th.build()
    th.compute()

    print('________________Three Shell Design Results_________________')
    print(f"Throughput {th.throughput_Gbps} Gbps")
    print('____________________________________________________________')

    pd.DataFrame(
        [{'gbps': th.throughput_Gbps}]
    ).to_csv(
        os.path.join(PREFIX_PATH, f'{prefix}_three_shell_design.csv'),
        index=False
    )


if __name__ == "__main__":

    PREFIX_PATH = 'experiments/results/plot_for_paper/CSVs/multi_shell_design'

    STARLINK = 'STARLINK'
    TOTAL_SAT_STARLINK_SHELL_1 = 72*22
    TOTAL_SAT_STARLINK_SHELL_2 = 72*22
    TOTAL_SAT_STARLINK_SHELL_3 = 36*20
    ALTITUDE_STARLINK_SHELL_1 = 550
    ALTITUDE_STARLINK_SHELL_2 = 540
    ALTITUDE_STARLINK_SHELL_3 = 570

    KUIPER = 'KUIPER'
    TOTAL_SAT_KUIPER_SHELL_1 = 34*34
    TOTAL_SAT_KUIPER_SHELL_2 = 36*36
    TOTAL_SAT_KUIPER_SHELL_3 = 28*28
    ALTITUDE_KUIPER_SHELL_1 = 630
    ALTITUDE_KUIPER_SHELL_2 = 610
    ALTITUDE_KUIPER_SHELL_3 = 590

    evaulate_single_shell_design(
        [TOTAL_SAT_KUIPER_SHELL_1, TOTAL_SAT_KUIPER_SHELL_2, TOTAL_SAT_KUIPER_SHELL_3],
        [ALTITUDE_KUIPER_SHELL_1, ALTITUDE_KUIPER_SHELL_2, ALTITUDE_KUIPER_SHELL_3],
        KUIPER
    )

    evaulate_two_shell_design(
        [TOTAL_SAT_KUIPER_SHELL_1, TOTAL_SAT_KUIPER_SHELL_2, TOTAL_SAT_KUIPER_SHELL_3],
        [ALTITUDE_KUIPER_SHELL_1, ALTITUDE_KUIPER_SHELL_2, ALTITUDE_KUIPER_SHELL_3],
        KUIPER
    )

    evaulate_three_shell_design(
        [TOTAL_SAT_KUIPER_SHELL_1, TOTAL_SAT_KUIPER_SHELL_2, TOTAL_SAT_KUIPER_SHELL_3],
        [ALTITUDE_KUIPER_SHELL_1, ALTITUDE_KUIPER_SHELL_2, ALTITUDE_KUIPER_SHELL_3],
        KUIPER
    )

    evaulate_single_shell_design(
        [TOTAL_SAT_STARLINK_SHELL_1, TOTAL_SAT_STARLINK_SHELL_2,
            TOTAL_SAT_STARLINK_SHELL_3],
        [ALTITUDE_STARLINK_SHELL_1, ALTITUDE_STARLINK_SHELL_2,
            ALTITUDE_STARLINK_SHELL_3],
        STARLINK
    )
    evaulate_two_shell_design(
        [TOTAL_SAT_STARLINK_SHELL_1, TOTAL_SAT_STARLINK_SHELL_2,
            TOTAL_SAT_STARLINK_SHELL_3],
        [ALTITUDE_STARLINK_SHELL_1, ALTITUDE_STARLINK_SHELL_2,
            ALTITUDE_STARLINK_SHELL_3],
        STARLINK
    )
    evaulate_three_shell_design(
        [TOTAL_SAT_STARLINK_SHELL_1, TOTAL_SAT_STARLINK_SHELL_2,
            TOTAL_SAT_STARLINK_SHELL_3],
        [ALTITUDE_STARLINK_SHELL_1, ALTITUDE_STARLINK_SHELL_2,
            ALTITUDE_STARLINK_SHELL_3],
        STARLINK
    )
