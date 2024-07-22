import copy
import heapq
import itertools
import random
import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import ProcessingLog


class PerformanceHeap:
    'Max heap for performance metrices. Works as priority queue for BFS'

    def __init__(self) -> None:
        self._max_heap: list[tuple[float, dict[str, float | int]]] = list()
        self.v = ProcessingLog(self.__class__.__name__)

    def add_new_item(self, performance_metrics: dict[str, float | int]) -> None:
        '''
        Push into max heap

        Parameters
        ----------
        performance_metrics: dict[str, float | int]
        '''

        heapq.heappush(
            self._max_heap,
            (
                -1 * performance_metrics.get('throughput_Gbps'),
                performance_metrics
            )
        )
        self.v.log(f'[add_heap] size: {len(self._max_heap)}')

    def pop_item(self) -> dict[str, float | int]:
        '''
        Pop from the max heap

        Returns
        ------
        dict[str, float | int]
            Maximum performane metrics or None if empty

        '''
        if not len(self._max_heap):
            self.v.log('[heap_error] Empty')
            return None

        _, performance_metrics = heapq.heappop(self._max_heap)
        self.v.log(f'[pop_heap] size: {len(self._max_heap)}')

        return performance_metrics


class BestFirstSearch:
    '''
    Optimizes angle of elevation (e), Altitude (h) and inclination (i) with Best First Search (Informed Search)

    Standard tuple of LEO params
    - ['0', '1', '2', '3', '4', '5']
    - ['e', 'h', 'i', 'n', 'o', 'p']
    '''

    def __init__(self, e: float, h: float, i: float, n: int, o: int, p: float) -> None:
        '''
        Starting point of the LEO parameters

        Parameters
        ----------
        e: float,
            Angle of elevation

        h: float
            Altitude in km

        i: float
            Inclination in degree

        n: int
            Number of sat per orbit

        o: int
            Number of orbits

        p: float
            Phase offset
        '''

        self.v = ProcessingLog(self.__class__.__name__)

        # Standard tuple of LEO params
        # ['0', '1', '2', '3', '4', '5']
        # ['e', 'h', 'i', 'n', 'o', 'p']

        # Current position in search space
        self._current_state = [
            round(float(e), 1),
            round(float(h), 1),
            round(float(i), 1),
            int(n), int(o),
            round(float(p), 1)
        ]

        # Step size towads each direction (e, h, i)
        self._steps = (5.0, 5.0, 5.0)

        # Legal range of the params
        self._bounds = [
            (5.0, 50.0),        # e
            (300.0, 2000),      # h
            (5.0, 90.0)         # i
        ]

        # Visited states to filter duplicate states
        self._visited_set = set()
        # Priority queue
        self._heap = PerformanceHeap()

    def set_e_bound(self, lb: float, ub: float) -> None:
        '''
        Set upper and lower and bound for AoE (e) degree

        Parameters
        ----------
        lb: float
            Lower bound

        ub: float
            Upper bound
        '''
        self._bounds[0] = (lb, ub)

    def set_h_bound(self, lb: float, ub: float) -> None:
        '''
        Set upper and lower and bound for altitude (h) km

        Parameters
        ----------
        lb: float
            Lower bound

        ub: float
            Upper bound
        '''
        self._bounds[1] = (lb, ub)

    def set_i_bound(self, lb: float, ub: float) -> None:
        '''
        Set upper and lower and bound for inclination (i) degree

        Parameters
        ----------
        lb: float
            Lower bound

        ub: float
            Upper bound
        '''
        self._bounds[2] = (lb, ub)

    def set_max_step_size(self, estep: int = 5, hstep: int = 5, istep: int = 5) -> None:
        '''
        Set step size of each dimension (e, h, i)

        Paramters
        ---------
        estep: int, optional
            Step size for AoE

        hstep: int, optional
            Step size for altitude

        istep: int, optional
            Step size for Inclination
        '''
        self._steps = (estep, hstep, istep)

    def _bound(self, params: list[float]) -> list[float]:
        '''
        Bound out of range parameters

        Parameters
        ----------
        params: list[float]
            LEO design parameters tuple

        Returns
        -------
        list[float]
            Bounded parameters
        '''

        for index, bound in enumerate(self._bounds):
            lb, ub = bound
            if params[index] < lb:
                params[index] = lb
            elif params[index] > ub:
                params[index] = ub

        return params

    def _generate_moves(self) -> None:
        'Generate all possible moves'

        self._moves = list()

        # Creating all possible combination of moves

        # Total 3D: e, h, i
        for num_of_direction in range(1, 4):
            for direction_indices in itertools.combinations(
                [0, 1, 2], num_of_direction
            ):
                # print(direction_indices)

                move = list()
                for index in [0, 1, 2]:
                    move.append(
                        self._steps[index] if index in direction_indices else 0
                    )

                # print(move)
                self._moves.append(move)

    def _hash(self, params: list) -> str:
        '''Generate the hash of LEO params

        Returns
        -------
        str
            Hash of LEO params
        '''
        return f'{params[0]}_{params[2]}_{params[1]}'

    def _generate_next_unique_states(self) -> list[list[float]]:
        '''
        Generate list of LEO paramters according to the moves possible from the current state

        Returns
        -------
        list[list[float]]
            Unique LEO params (not in visited set)
        '''

        next_unique_states = list()

        # print(self._current_state)
        for move in self._moves:
            # print(move)

            # Forward and backward moves from the current states
            forward_state = copy.deepcopy(self._current_state)
            backward_state = copy.deepcopy(self._current_state)
            for index, step in enumerate(move):
                # forward_state[index] += step
                # backward_state[index] -= step

                forward_state[index] += round((step * random.random()), 1)
                backward_state[index] -= round((step * random.random()), 1)

            # Fixing out of bound params
            forward_state = self._bound(forward_state)
            backward_state = self._bound(backward_state)

            # Filtering unique params
            for state in [forward_state, backward_state]:
                _hash = self._hash(state)

                if _hash not in self._visited_set:
                    # print(state)
                    next_unique_states.append(state)
                    self._visited_set.add(_hash)

        return next_unique_states

    def _dict_to_tuple(self, performance_metrics: dict[str, float | int]) -> list[float]:
        '''
        Extract ordered LEO parameters from performance metrics

        Parameters
        ----------
        performance_metrics: dict[str, float | int]
            Performance metrics

        Returns
        -------
        list[float]
            Ordered LEO params
        '''

        return [
            performance_metrics.get('S0_e'),
            performance_metrics.get('S0_h_km'),
            performance_metrics.get('S0_i'),
            performance_metrics.get('S0_n'),
            performance_metrics.get('S0_o'),
            performance_metrics.get('S0_p')
        ]

    def _simulate_states(self, states: list[list[float]]) -> None:
        '''
        Simulate a set of LEO parameters and insert performance metrics into the max heap

        Parameters
        ----------
        states: list[list[float]]
            List of LEO parameters
        '''

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

        # Simulation setup
        simulator = LEOConstellationSimulator(
            InternetTrafficAcrossCities.ONLY_POP_100
        )

        # Adding all the LEO constellations
        for state in states:

            leo_con = LEOConstellation()
            leo_con.add_ground_stations(GroundStation(
                GroundStationAtCities.TOP_100
            ))
            leo_con.set_time()
            leo_con.set_loss_model(get_loss_model())

            # Standard tuple of LEO params
            # ['0', '1', '2', '3', '4', '5']
            # ['e', 'h', 'i', 'n', 'o', 'p']

            leo_con.add_shells(PlusGridShell(
                id=0,

                orbits=state[4],
                sat_per_orbit=state[3],
                phase_offset=state[5],

                altitude_m=state[1]*1000,
                angle_of_elevation_degree=state[0],
                inclination_degree=state[2]
            ))

            simulator.add_constellation(leo_con)

        # Simulate all the constellation design
        # simulator.simulate_in_serial()
        performance_logs = simulator.simulate_in_parallel(max_workers=3)

        # Add the perfomance metrics to max heap
        for performance_log in performance_logs:
            self._heap.add_new_item(performance_log)

    def _update_current_state(self) -> dict[str, float | int]:
        '''
        Update current state with maximum throughput from the priority queue

        Returns
        -------
        dict[str, float | int]
            Performance metrics popped from max heap
        '''
        performance_metrics = self._heap.pop_item()
        self._current_state = self._dict_to_tuple(performance_metrics)
        return performance_metrics

    def search(self, max_iter: int = 100, tolerance: int = 5) -> dict[str, float | int]:
        '''
        Execute Best First Search from the current state

        Parameters
        ----------
        max_iter: int, optional
            Maximum number of iteration (default 15)
        tolerance: int. optional
            Maximum number of consecutive performance fall


        Returns
        -------
        dict[str, float | int]
            Best perfomance metrics after termination of Best First Search
        '''

        start_time = time.perf_counter()

        best_performance = {'throughput_Gbps': 0}
        remaining_fall_tolerance = tolerance
        self._generate_moves()

        while max_iter and remaining_fall_tolerance:

            print('_'*100, 'Iter START:', max_iter)

            next_unique_states = self._generate_next_unique_states()
            self._simulate_states(next_unique_states)
            performance_metrics = self._update_current_state()

            if performance_metrics.get('throughput_Gbps') > best_performance.get('throughput_Gbps'):
                best_performance = performance_metrics
                remaining_fall_tolerance = tolerance
                self.v.log(f'Tolerance up: {remaining_fall_tolerance}')
            else:
                remaining_fall_tolerance -= 1
                self.v.log(f'Tolerance fall: {remaining_fall_tolerance}')

            self.v.log(
                f"""[CURRENT STATE] {
                    self.__extract_state_info(performance_metrics)}"""
            )
            self.v.log(
                f"""[BEST STATE] {
                    self.__extract_state_info(best_performance)}"""
            )

            print('_'*100, 'Iter END:', max_iter)
            max_iter -= 1

        end_time = time.perf_counter()

        self.v.log(f"""[BEST STATE] {
                   self.__extract_state_info(best_performance)}""")
        self.v.log(f'Total BFS time: {round((end_time-start_time)/60, 1)}m')

        return self.__standard_dict_format(best_performance)

    def __extract_state_info(self, metrics: dict[str, float | int]) -> str:
        return f"""h{metrics.get('S0_h_km')} e{metrics.get('S0_e')} i{metrics.get('S0_i')} | o{metrics.get('S0_o')} n{metrics.get('S0_n')} p{metrics.get('S0_p')} \t th: {round(metrics.get('throughput_Gbps'), 1)}Gbps"""

    def __standard_dict_format(self, metrics: dict[str, float | int]) -> dict[str, float | int]:
        return {
            'o': metrics.get('S0_o'), 'n': metrics.get('S0_n'),

            'h': round(metrics.get('S0_h_km'), 1),
            'i': round(metrics.get('S0_i'), 1),
            'e': round(metrics.get('S0_e'), 1),
            'p': round(metrics.get('S0_p'), 1),

            'gbps': metrics.get('throughput_Gbps')
        }
