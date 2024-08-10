import time

import numpy as np
import scipy.optimize

from experiments.blackbox_optimization.common import *
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import CSV_logger


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
    _leo_con = LEOConstellation('COST_FUN', PARALLEL_MODE=False)
    _leo_con.v.verbose = False
    _leo_con.add_ground_stations(GroundStation(GROUND_STATIONS))
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
    print(f''' > o: {o}, n: {n}, h: {
        h/1000}, e: {e}, i: {i}, p: {p} \t|=>\t COST: {cost}''')

    return cost


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
    _leo_con = LEOConstellation('COST_FUN', PARALLEL_MODE=False)
    _leo_con.v.verbose = False
    _leo_con.add_ground_stations(GroundStation(GROUND_STATIONS))
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
    print(f''' > o: {o}, n: {n}, h: {
        h/1000}, e: {e}, i: {i}, p: {p} \t|=>\t COST: {cost}''')

    return cost


def with_domain_knowledge() -> dict[str, float | int]:

    # Standard tuple of LEO params
    # - ['0', '1', '2']
    # - ['e', 'h', 'i']
    bounds = (
        [5.0, 50.0],                        # e (degree)
        [ALTITUDE_LB_KM, ALTITUDE_UB_KM],   # h (km)
        [30.0, 90.0],                       # i (degree)
    )

    result = scipy.optimize.differential_evolution(
        _cost_with_domain_knowledge, bounds,

        workers=-1,
        updating='deferred'
    )
    print('_'*99)
    print(result)
    print(f'''
        o , n = {OXN[-1]}
        h = {round(result.x[1], 1)}
        i = {round(result.x[2], 1)}
        e = {round(result.x[0], 1)}
        p = 50.0
    ''')

    return {
        'o': OXN[-1][0], 'n': OXN[-1][1],

        'h': round(result.x[1], 1),
        'i': round(result.x[2], 1),
        'e': round(result.x[0], 1),
        'p': 50.0,

        'gbps': result.fun*-1
    }


def without_domain_knowledge() -> dict[str, float | int]:
    # Standard tuple of LEO params
    # - ['0', '1', '2', '3', '4']
    # - ['e', 'h', 'i', 'o', 'p']
    bounds = (
        [0.0, 90.0],                        # e (degree)
        [ALTITUDE_LB_KM, ALTITUDE_UB_KM],   # h (km)
        [0.0, 180.0],                       # i (degree)
        [0, len(OXN)-1],                    # index of oxn arrangment
        [0.0, 50.0]                         # P (%)
    )

    result = scipy.optimize.differential_evolution(
        _cost_without_domain_knowledge, bounds,

        workers=-1,
        updating='deferred'
    )

    print('_'*99)
    print(result)
    print(f'''
        o , n = {OXN[round(result.x[3])]}
        h = {round(result.x[1], 1)}
        i = {round(result.x[2], 1)}
        e = {round(result.x[0], 1)}
        p = {round(result.x[4], 2)}
    ''')

    return {
        'o': OXN[round(result.x[3])][0],
        'n': OXN[round(result.x[3])][1],

        'h': round(result.x[1], 1),
        'i': round(result.x[2], 1),
        'e': round(result.x[0], 1),
        'p': round(result.x[4], 2),

        'gbps': result.fun*-1
    }


if __name__ == '__main__':
    TOTAL_SATS = 720
    MIN_SAT_PER_ORBIT = 10
    ALTITUDE_UB_KM = 575
    ALTITUDE_LB_KM = 565

    GROUND_STATIONS = GroundStationAtCities.TOP_100
    TRAFFIC_METRICE = InternetTrafficAcrossCities.ONLY_POP_100
    OXN = get_possible_oxn_arrangements(TOTAL_SATS, MIN_SAT_PER_ORBIT)

    cache = PerformanceCache()
    _start_time = time.perf_counter()

    # CSV = 'DE_WDK.csv'
    # result = without_domain_knowledge()

    CSV = 'DE_DK.csv'
    result = with_domain_knowledge()

    _end_time = time.perf_counter()
    print(f"""Total optimization time: {
        round((_end_time-_start_time)/3600, 2)}h""")
    result['time_s'] = _end_time-_start_time
    result['total_sat'] = TOTAL_SATS
    CSV_logger(result, CSV)
