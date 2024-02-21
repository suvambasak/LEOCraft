from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.performance.aviation.coverage import Coverage
from LEOCraft.performance.aviation.stretch import Stretch
from LEOCraft.performance.aviation.throughput import Throughput
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator


class LEOAviationConstellationSimulator(LEOConstellationSimulator):

    def _measure_performance(self, leo_con: LEOAviationConstellation) -> dict[str, float | int]:
        '''Computes the Throughput, Coverage, and Stretch of the constellation then generate performance dataset

        Parameters:
        -------
        leo_con: LEOAviationConstellation
            Object of LEOAviationConstellation

        Returns
        ------
        dict[str, float | int]
            Performance dataset in dict formatX
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

        performane_log = dict()

        performane_log = self._leo_param_to_dict(leo_con)
        performane_log = self._add_throughput_to_dict(th, performane_log)
        performane_log = self._add_coverage_to_dict(cov, performane_log)
        performane_log = self._add_stretch_to_dict(sth, performane_log)

        return performane_log

    def _add_coverage_to_dict(self, cov: Coverage, performane_log: dict[str, float | int]) -> dict[str, float | int]:
        performane_log['dead_GS_count'] = cov.dead_GS_count
        performane_log['GS_coverage_metric'] = cov.GS_coverage_metric
        performane_log['dead_flight_count'] = cov.dead_flight_count
        performane_log['flight_coverage_metric'] = cov.flight_coverage_metric

        return performane_log
