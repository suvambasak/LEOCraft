import concurrent.futures
import time

import numpy as np

from experiments.blackbox_optimization.common import *
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import CSV_logger


def parallel_cost(cost_fun: callable, particle: np.ndarray, index: int) -> tuple[float, int]:
    return cost_fun(particle), index


def adaptive_particle_swarm_optimization(
        maxiter: int,
        num_particles: int,

        lb: np.ndarray,
        ub: np.ndarray,
        num_of_params: int,

        cost_fun: callable
) -> tuple[np.ndarray, np.float64]:

    # # Adaptive Parameters
    # w_start, w_end = 0.9, 0.4
    # c1_start, c1_end = 2.5, 0.5
    # c2_start, c2_end = 0.5, 2.5

    # Auto hyperparameters
    # Sermpinis, Georgios, et al. "Forecasting foreign exchange rates with adaptive neural networks using radial-basis functions and particle swarm optimization." European Journal of Operational Research 225.3 (2013): 528-540.
    w, c1, c2 = 0.8, 3.5, 0.5

    # Initialize particles
    particles = np.random.uniform(
        low=lb, high=ub,
        size=(num_particles, num_of_params)
    )
    # Initialize velocities with +/-5 step size
    velocities = np.random.uniform(
        low=-5, high=5,
        size=(num_particles, num_of_params)
    )

    # Start A-PSO

    # # Serial mode
    # --------------------
    # personal_best_values = np.array(
    #     [cost_fun(particle)[0] for particle in particles]
    # )
    # --------------------

    # Parallel mode
    # --------------------
    tasks = set()
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

        # Evaulate in parallel
        for i, particle in enumerate(particles):
            tasks.add(executor.submit(parallel_cost, cost_fun, particle, i))

        _personal_best_values = [None]*num_particles
        for compute in concurrent.futures.as_completed(tasks):
            _personal_best_value, _index = compute.result()
            _personal_best_values[_index] = _personal_best_value
    # --------------------

    personal_best_values = np.array(_personal_best_values)
    personal_best_positions = np.copy(particles)

    global_best_value = np.min(personal_best_values)
    global_best_position = personal_best_positions[
        np.argmin(personal_best_values)
    ]

    # PSO main loop
    for iter in range(maxiter):

        # # Update inertia weight
        # w = w_start - ((w_start - w_end) / maxiter) * iter
        # # Update cognitive and social coefficients
        # c1 = c1_start - ((c1_start - c1_end) / maxiter) * iter
        # c2 = c2_start + ((c2_end - c2_start) / maxiter) * iter

        # Auto hyperparameters
        # Sermpinis, Georgios, et al. "Forecasting foreign exchange rates with adaptive neural networks using radial-basis functions and particle swarm optimization." European Journal of Operational Research 225.3 (2013): 528-540.
        # Update inertia weight
        w = (0.4/maxiter**2) * (iter - maxiter) ** 2 + 0.4
        # Update cognitive and social coefficients
        c1 = -3 * iter / maxiter + 3.5
        c2 = 3 * iter / maxiter + 0.5

        print('\n_______________________________________________________ Iter:', iter+1)
        print(f' [Hyperparameters]\tw: {w}, c1: {c1}, c2: {c2}')

        # # Serial mode
        # # --------------------
        # for i in range(num_particles):
        #     r1, r2 = np.random.rand(
        #         num_of_params), np.random.rand(num_of_params)
        #     velocities[i] = (w * velocities[i] +
        #                      c1 * r1 * (personal_best_positions[i] - particles[i]) +
        #                      c2 * r2 * (global_best_position - particles[i]))
        #     particles[i] += velocities[i]

        #     # Boundary handling
        #     particles[i] = np.clip(particles[i], lb, ub)

        #     # Update personal bests
        #     current_value = cost_fun(particles[i])[0]
        #     if current_value < personal_best_values[i]:
        #         personal_best_values[i] = current_value
        #         personal_best_positions[i] = particles[i]
        # # --------------------

        # Parallel mode
        # --------------------
        tasks = set()
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for i in range(num_particles):
                r1, r2 = np.random.rand(
                    num_of_params), np.random.rand(num_of_params)

                velocities[i] = (w * velocities[i] + c1 * r1 * (personal_best_positions[i] -
                                 particles[i]) + c2 * r2 * (global_best_position - particles[i]))
                particles[i] += velocities[i]

                # Boundary handling
                particles[i] = np.clip(particles[i], lb, ub)

                # Evaulate in parallel
                tasks.add(executor.submit(
                    parallel_cost, cost_fun, particles[i], i
                ))

            # Update personal bests
            for compute in concurrent.futures.as_completed(tasks):
                _value, _index = compute.result()

                if _value < personal_best_values[_index]:
                    personal_best_values[_index] = _value
                    personal_best_positions[_index] = particles[_index]
        # --------------------

        # Update global best
        best_particle_index = np.argmin(personal_best_values)
        if personal_best_values[best_particle_index] < global_best_value:
            global_best_value = personal_best_values[best_particle_index]
            global_best_position = personal_best_positions[best_particle_index]

    return global_best_position, global_best_value


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
    print(f'''  o: {o}, n: {n}, h: {
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
    _leo_con = LEOConstellation('COST_FUN', PARALLEL_MODE=True)
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


def without_domain_knowledge(maxiter: int, num_particles: int) -> dict[str, float | int]:

    # Define the bounds of the search space for each dimension
    # Standard tuple of LEO params
    # - ['0', '1', '2', '3', '4']
    # - ['e', 'h', 'i', 'o', 'p']

    # Lower bounds
    lb = np.array([1.0, ALTITUDE_LB_KM, 0.0, 0, 0.0])
    # Upper bounds
    ub = np.array([90.0, ALTITUDE_UB_KM, 180.0, len(OXN)-1, 50.0])

    global_best_position, global_best_value = adaptive_particle_swarm_optimization(
        maxiter, num_particles,
        lb, ub, len(lb),
        _cost_without_domain_knowledge
    )

    # Results
    print('_'*99)
    print(f'Throughput: {-1 * global_best_value}')
    print(f'''
        o , n = {OXN[round(global_best_position[3])]}
        h = {round(global_best_position[1], 1)}
        i = {round(global_best_position[2], 1)}
        e = {round(global_best_position[0], 1)}
        p = {round(global_best_position[4], 2)}
    ''')

    return {
        'o': OXN[round(global_best_position[3])][0],
        'n': OXN[round(global_best_position[3])][1],

        'h': round(global_best_position[1], 1),
        'i': round(global_best_position[2], 1),
        'e': round(global_best_position[0], 1),
        'p': round(global_best_position[4], 2),

        'gbps': global_best_value*-1
    }


def with_domain_knowledge(maxiter: int, num_particles: int) -> dict[str, float | int]:

    # Define the bounds of the search space for each dimension
    # Standard tuple of LEO params
    # - ['0', '1', '2']
    # - ['e', 'h', 'i']
    lb = np.array([5.0, ALTITUDE_LB_KM, 30.0])      # Lower bounds
    ub = np.array([50.0, ALTITUDE_UB_KM, 90.0])     # Upper bounds

    global_best_position, global_best_value = adaptive_particle_swarm_optimization(
        maxiter, num_particles,
        lb, ub, len(lb),
        _cost_with_domain_knowledge
    )

    # Results
    print('_'*99)
    print(f'Throughput: {-1 * global_best_value}')
    print(f'''
        o , n = {OXN[-1]}
        h = {round(global_best_position[1], 1)}
        i = {round(global_best_position[2], 1)}
        e = {round(global_best_position[0], 1)}
        p = 50.0
    ''')

    return {
        'o': OXN[-1][0], 'n': OXN[-1][1],

        'h': round(global_best_position[1], 1),
        'i': round(global_best_position[2], 1),
        'e': round(global_best_position[0], 1),
        'p': 50.0,

        'gbps': global_best_value*-1
    }


if __name__ == '__main__':
    TOTAL_SATS = 720
    MIN_SAT_PER_ORBIT = 10
    ALTITUDE_UB_KM = 570+5
    ALTITUDE_LB_KM = 570-5

    GROUND_STATIONS = GroundStationAtCities.TOP_100
    TRAFFIC_METRICE = InternetTrafficAcrossCities.ONLY_POP_100
    OXN = get_possible_oxn_arrangements(TOTAL_SATS, MIN_SAT_PER_ORBIT)

    MAX_WORKERS = 3
    cache = PerformanceCache()
    _start_time = time.perf_counter()

    CSV = 'PSO_WDK.csv'
    result = without_domain_knowledge(maxiter=25, num_particles=20)

    # CSV = 'PSO_DK.csv'
    # result = with_domain_knowledge(maxiter=25, num_particles=10)

    _end_time = time.perf_counter()
    print(f"""Total optimization time: {
        round((_end_time-_start_time)/3600, 2)}h""")
    result['time_s'] = _end_time-_start_time
    result['total_sat'] = TOTAL_SATS
    CSV_logger(result, CSV)
