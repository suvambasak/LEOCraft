import time

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.basic.stretch import Stretch
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.simulator.simulator import Simulator


class LEOConstellationSimulator(Simulator):

    def _simulate(self, leo_con: LEOConstellation) -> tuple[dict[str, float | int], float]:
        start_time = time.perf_counter()

        leo_con.build()
        leo_con.create_network_graph()
        leo_con.generate_routes()
        performane_log = self._measure_performance(leo_con)

        end_time = time.perf_counter()
        return performane_log, round((end_time-start_time)/60, 2)

    def _measure_performance(self, leo_con: LEOConstellation) -> dict[str, float | int]:
        '''Computes the Throughput, Coverage, and Stretch of the constellation then generate performance dataset

        Parameters:
        -------
        leo_con: LEOConstellation
            Object of LEOConstellation

        Returns
        ------
        dict[str, float | int]
            Performance dataset in dict format
        '''

        th = Throughput(leo_con, self._traffic_metrics)
        th.v.verbose = False
        th.build()
        th.compute()

        cov = Coverage(leo_con)
        cov.v.verbose = False
        cov.build()
        cov.compute()

        sth = Stretch(leo_con)
        sth.v.verbose = False
        sth.build()
        sth.compute()

        performane_log = self._leo_param_to_dict(leo_con)
        performane_log = self._add_throughput_to_dict(th, performane_log)
        performane_log = self._add_coverage_to_dict(cov, performane_log)
        performane_log = self._add_stretch_to_dict(sth, performane_log)

        return performane_log
