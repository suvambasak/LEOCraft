import time

import numpy as np
import scipy.optimize
from LEOCraft_env import *

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation


def get_loss_model() -> FSPL:
    'Path loass model'

    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


def simulated_annealing_without_domain_knowledge(no_local_search: bool) -> None:

    def _cost_without_domain_knowledge(x: np.ndarray) -> float:
        '''
        Standard tuple of LEO params
        - ['0', '1', '2', '3', '4']
        - ['e', 'h', 'i', 'o', 'p']
        '''

        e = round(x[0], 1)
        h = round(x[1]) * 1000  # in meters
        i = round(x[2], 1)
        o, n = OXN[round(x[3])]
        p = round(x[4])

        key = f"e{e}_h{h}_i{i}_o{o}_n{n}_p{p}"
        cost = cache.get(key)
        if cost is not None:
            return cost

        # Create constellation
        _leo_con = LEOConstellation('COST_FUN', PARALLEL_MODE=True)
        _leo_con.v.verbose = False
        _leo_con.add_ground_stations(
            GroundStation(GroundStationAtCities.TOP_100))
        _leo_con.add_shells(PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            altitude_m=h,
            inclination_degree=i,
            angle_of_elevation_degree=e,
            phase_offset=p
        ))
        _leo_con.set_time()
        _leo_con.set_loss_model(get_loss_model())
        _leo_con.build()
        _leo_con.create_network_graph()
        _leo_con.generate_routes()

        # Throughput
        _th = Throughput(_leo_con, TRAFFIC_METRICE)
        _th.v.verbose = False
        _th.build()
        _th.compute()

        cost = -1 * _th.throughput_Gbps
        cache.add(key, cost)
        print(f'''  o: {o}, n: {n}, h: {
            h/1000}, e: {e}, i: {i}, p: {p} \t|=>\t COST: {cost}''')

        return cost

    def _without_domain_knowledge_results(result: scipy.optimize.OptimizeResult) -> None:
        print('='*99)
        print(result)
        print(f'''
            o , n = {OXN[round(result.x[3])]}
            h = {round(result.x[1], 1)}
            i = {round(result.x[2], 1)}
            e = {round(result.x[0], 1)}
            p = {round(result.x[4], 2)}
        ''')

    # Standard tuple of LEO params
    # - ['0', '1', '2', '3', '4']
    # - ['e', 'h', 'i', 'o', 'p']
    bounds = (
        [5.0, 50.0],        # e (degree)
        [ALTITUDE_LB_KM, ALTITUDE_UB_KM],   # h (km)
        [30.0, 90.0],       # i (degree)
        [0, len(OXN)-1],    # index of oxn arrangment
        [0.0, 50.0]         # P (%)
    )

    result = scipy.optimize.dual_annealing(
        _cost_without_domain_knowledge, bounds,
        no_local_search=no_local_search
    )
    _without_domain_knowledge_results(result)


def simulated_annealing_with_domain_knowledge(no_local_search: bool) -> None:

    def _cost_with_domain_knowledge(x: np.ndarray) -> float:
        '''
        Standard tuple of LEO params
        - ['0', '1', '2']
        - ['e', 'h', 'i']
        '''

        e = round(x[0], 1)
        h = round(x[1]) * 1000  # in meters
        i = round(x[2], 1)

        o, n = OXN[-1]
        p = 50.0

        key = f"e{e}_h{h}_i{i}_o{o}_n{n}_p{p}"
        cost = cache.get(key)
        if cost is not None:
            return cost

        # Create constellation
        _leo_con = LEOConstellation('COST_FUN', PARALLEL_MODE=True)
        _leo_con.v.verbose = False
        _leo_con.add_ground_stations(
            GroundStation(GroundStationAtCities.TOP_100))
        _leo_con.add_shells(PlusGridShell(
            id=0,
            orbits=o,
            sat_per_orbit=n,
            altitude_m=h,
            inclination_degree=i,
            angle_of_elevation_degree=e,
            phase_offset=p
        ))
        _leo_con.set_time()
        _leo_con.set_loss_model(get_loss_model())
        _leo_con.build()
        _leo_con.create_network_graph()
        _leo_con.generate_routes()

        # Throughput
        _th = Throughput(_leo_con, TRAFFIC_METRICE)
        _th.v.verbose = False
        _th.build()
        _th.compute()

        cost = -1 * _th.throughput_Gbps
        cache.add(key, cost)
        print(f'''  o: {o}, n: {n}, h: {
            h/1000}, e: {e}, i: {i}, p: {p} \t|=>\t COST: {cost}''')

        return cost

    def _with_domain_knowledge_results(result: scipy.optimize.OptimizeResult) -> None:
        print('='*99)
        print(result)
        print(f'''
            o , n = {OXN[-1]}
            h = {round(result.x[1], 1)}
            i = {round(result.x[2], 1)}
            e = {round(result.x[0], 1)}
            p = 50.0
        ''')

    # Standard tuple of LEO params
    # - ['0', '1', '2']
    # - ['e', 'h', 'i']
    bounds = (
        [5.0, 50.0],                        # e (degree)
        [ALTITUDE_LB_KM, ALTITUDE_UB_KM],   # h (km)
        [30.0, 90.0],                       # i (degree)
    )

    result = scipy.optimize.dual_annealing(
        _cost_with_domain_knowledge, bounds,
        no_local_search=no_local_search
    )
    _with_domain_knowledge_results(result)


if __name__ == '__main__':
    TOTAL_SATS = 28**2
    MIN_SAT_PER_ORBIT = 10
    ALTITUDE_UB_KM = 600
    ALTITUDE_LB_KM = 590

    GROUND_STATIONS = GroundStationAtCities.TOP_100
    TRAFFIC_METRICE = InternetTrafficAcrossCities.ONLY_POP_100
    OXN = get_possible_oxn_arrangements(TOTAL_SATS, MIN_SAT_PER_ORBIT)

    cache = PerformanceCache()

    _start_time = time.perf_counter()
    # simulated_annealing_without_domain_knowledge(no_local_search=True)
    simulated_annealing_with_domain_knowledge(no_local_search=True)
    _end_time = time.perf_counter()

    print(f'Total optimization time: {round((_end_time-_start_time)/60, 2)}m')
