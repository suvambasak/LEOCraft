import concurrent.futures
import os
import time
from abc import ABC, abstractmethod

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.stretch import Stretch
from LEOCraft.performance.throughput_LP import ThroughputLP
from LEOCraft.utilities import CSV_logger, ProcessingLog


class Simulator(ABC):
    '''Abstract class for execution of batch simulation in parallel/serial mode. 
    The performance data of simulation are logged into CSV file. 
    All the constellation simulator are subclass of Simulator
    '''

    def __init__(self, traffic_metrics: str, csv_file: str | None = None) -> None:
        self.v = ProcessingLog(self.__class__.__name__)

        self._traffic_metrics = traffic_metrics

        if csv_file:
            self._CSV = csv_file
        else:
            self._CSV = f'{self.__class__.__name__}.csv'

        self._simulation_jobs: set[Constellation] = set()
        self.max_workers: int

    def add_constellation(self, leo_con: Constellation) -> None:
        '''Add constellation job queue for simulation execution

        Parameters
        ----------
        leo_con: Constellation
            Object of a subclass of Constellation i.e., LEOConstellation, LEOAviationConstellation
        '''
        leo_con.v.verbose = False
        self._simulation_jobs.add(leo_con)

    def _simulation_progress(self, completed_count: int, _t_time: float) -> None:
        '''Show simulation progress log

        Parallel
        --------
        completed_count: int
            Number of simualtion completed
        _t_time: float
            Total time taken till now
        '''

        _progress = f'{completed_count}/{len(self._simulation_jobs)}'
        _left = len(self._simulation_jobs) - completed_count
        _avg_t = round(_t_time/completed_count, 2)
        _eta = round(_left*_avg_t/self.max_workers, 2)

        self.v.log(
            f'''Simulation progress: {_progress}  Left: {_left} Avg time: {
                _avg_t}m ETA: {_eta}m    '''
        )

    def simulate_in_serial(self):
        'Start simulation execution in serial (one by one)'

        self.v.log(
            f'''Starting {
                len(self._simulation_jobs)
            } simulation(s) in serial... '''
        )

        self.max_workers = 1

        start_time = time.perf_counter()
        _t_time = 0.0
        for completed_count, leo_con in enumerate(self._simulation_jobs):
            performane_log, __t = self._simulate(leo_con)

            _t_time += __t
            CSV_logger(performane_log, self._CSV)
            self._simulation_progress(completed_count+1, _t_time)

        end_time = time.perf_counter()
        self.v.log(
            f'''Total {len(self._simulation_jobs)} simulation(s) completed in: {
                round((end_time-start_time)/60, 2)}m     '''
        )

    def simulate_in_parallel(self, max_workers: int | None = None):
        '''Start simulation execution in parallel (by default as many CPU cores)

        Parameters
        --------
        max_workers: int | None, optional
            Maximum number of parallel process
        '''

        self.v.log(
            f'''Starting {len(
                self._simulation_jobs
            )} simulation(s) {max_workers} in parallel... '''
        )

        if max_workers:
            self.max_workers = max_workers
        else:
            self.max_workers = os.cpu_count()

        start_time = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            simulation_computes = {
                executor.submit(self._simulate, leo_con) for leo_con in self._simulation_jobs
            }

            _t_time = 0.0
            completed_count = 0
            for simulation_compute in concurrent.futures.as_completed(simulation_computes):
                completed_count += 1
                performane_log, __t = simulation_compute.result()

                _t_time += __t
                CSV_logger(performane_log, self._CSV)
                self._simulation_progress(completed_count, _t_time)

        end_time = time.perf_counter()
        self.v.log(
            f'''Total {len(self._simulation_jobs)} simulation(s) completed in: {
                round((end_time-start_time)/60, 2)}m       '''
        )

    def _leo_param_to_dict(self, leo_con: Constellation) -> dict[str, float | int]:
        '''Create a dict of the given leo constellation parameters

        Paramters
        ------
        leo_con: Constellation
            Object of a subclass of Constellation i.e., LEOConstellation, LEOAviationConstellation

        Returns
        ------
        dict[str, float | int]:
            Dict of LEO constellation parameters
        '''

        performane_log = dict()

        performane_log['time_delta'] = leo_con.time_delta
        for shell in leo_con.shells:
            performane_log[f'{shell.name}_o'] = shell.orbits
            performane_log[f'{shell.name}_n'] = shell.sat_per_orbit
            performane_log[f'{shell.name}_h_km'] = shell.altitude_m/1000
            performane_log[f'{shell.name}_i'] = shell.inclination_degree
            performane_log[f'{shell.name}_e'] = shell.angle_of_elevation_degree
            performane_log[f'{shell.name}_p'] = shell.phase_offset

        return performane_log

    def _add_throughput_to_dict(self, th: ThroughputLP, performane_log: dict[str, float | int]) -> dict[str, float | int]:
        '''Adds throughput metrics to performance log

        Parameters
        ---------
        th: ThroughputLP
            Instance of throughputLP subclass
        performane_log: dict[str, float | int]
            Performance log dict with param info

        Returns
        -------
        dict[str, float | int]
            Updated dict with throughput metrics
        '''

        performane_log['throughput_Gbps'] = th.throughput_Gbps
        performane_log['total_accommodated_flow'] = th.total_accommodated_flow

        performane_log['NS_selt'] = th.NS_selt
        performane_log['EW_selt'] = th.EW_selt
        performane_log['NESW_selt'] = th.NESW_selt
        performane_log['HG_selt'] = th.HG_selt
        performane_log['LG_selt'] = th.LG_selt

        return performane_log

    def _add_coverage_to_dict(self, cov: Coverage, performane_log: dict[str, float | int]) -> dict[str, float | int]:
        '''Adds throughput metrics to performance log

        Parameters
        ---------
        cov: Coverage
            Instance of Coverage class/subclass
        performane_log: dict[str, float | int]
            Performance log dict with param info

        Returns
        -------
        dict[str, float | int]
            Updated dict with coverage metrics
        '''

        performane_log['dead_GS_count'] = cov.dead_GS_count
        performane_log['GS_coverage_metric'] = cov.GS_coverage_metric

        return performane_log

    def _add_stretch_to_dict(self, sth: Stretch, performane_log: dict[str, float | int]) -> dict[str, float | int]:
        '''Adds throughput metrics to performance log

        Parameters
        ---------
        sth: Stretch,
            Instance of Stretch subclass
        performane_log: dict[str, float | int]
            Performance log dict with param info

        Returns
        -------
        dict[str, float | int]
            Updated dict with stretch metrics
        '''

        performane_log['NS_sth'] = sth.NS_sth
        performane_log['EW_sth'] = sth.EW_sth
        performane_log['HG_sth'] = sth.HG_sth
        performane_log['LG_sth'] = sth.LG_sth
        performane_log['NESW_sth'] = sth.NESW_sth

        performane_log['NS_cnt'] = sth.NS_cnt
        performane_log['EW_cnt'] = sth.EW_cnt
        performane_log['HG_cnt'] = sth.HG_cnt
        performane_log['LG_cnt'] = sth.LG_cnt
        performane_log['NESW_cnt'] = sth.NESW_cnt

        return performane_log

    @abstractmethod
    def _simulate(self, leo_con: Constellation) -> tuple[dict[str, float | int], float]:
        '''Simulate a constellation and measure the performance

        Parameters
        --------
        leo_con: Constellation
            Object of a subclass of Constellation i.e., LEOConstellation, LEOAviationConstellation

        Returns
        -------
        tuple[dict[str, float | int], float]
            Performance data in dict format and the time taken to complete simulation
        '''

        pass
