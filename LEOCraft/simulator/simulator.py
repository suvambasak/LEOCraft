import concurrent.futures
import os
import time
from abc import ABC, abstractmethod

from LEOCraft.constellations.constellation import Constellation
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

    def add_constellation(self, leo_con: Constellation) -> None:
        '''Add constellation job queue for simulation execution

        Parameters
        ----------
        leo_con: Constellation
            Object of a subclass of Constellation i.e., LEOConstellation, LEOAviationConstellation
        '''
        leo_con.v.verbose = False
        self._simulation_jobs.add(leo_con)

    def _simulation_progress(self, completed_count: int, _t_time: float, parallel_mode: bool = False) -> None:
        '''Show simulation progress log

        Parallel
        --------
        completed_count: int
            Number of simualtion completed
        _t_time: float
            Total time taken till now
        parallel_mode: bool, optional
            Execution mode of the simulations
        '''

        _progress = f'{completed_count}/{len(self._simulation_jobs)}'
        _left = len(self._simulation_jobs) - completed_count
        _avg_t = round(_t_time/completed_count, 2)

        if parallel_mode:
            _eta = round(_left*_avg_t/os.cpu_count(), 2)
        else:
            _eta = round(_left*_avg_t, 2)

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

    def simulate_in_parallel(self):
        'Start simulation execution in parallel (as many CPU cores)'

        self.v.log(
            f'''Starting {len(
                self._simulation_jobs
            )} simulation(s) in parallel... '''
        )

        start_time = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor() as executor:
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
                self._simulation_progress(completed_count, _t_time, True)

        end_time = time.perf_counter()
        self.v.log(
            f'''Total {len(self._simulation_jobs)} simulation(s) completed in: {
                round((end_time-start_time)/60, 2)}m       '''
        )

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
