
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

        performane_log = dict()

        performane_log['time_delta'] = leo_con.time_delta
        for shell in leo_con.shells:
            performane_log[f'{shell.name}_o'] = shell.orbits
            performane_log[f'{shell.name}_n'] = shell.sat_per_orbit
            performane_log[f'{shell.name}_h_km'] = shell.altitude_m/1000
            performane_log[f'{shell.name}_i'] = shell.inclination_degree
            performane_log[f'{shell.name}_e'] = shell.angle_of_elevation_degree
            performane_log[f'{shell.name}_p'] = shell.phase_offset

        performane_log['throughput_Gbps'] = th.throughput_Gbps
        performane_log['total_accommodated_flow'] = th.total_accommodated_flow
        performane_log['NS_selt'] = th.NS_selt
        performane_log['EW_selt'] = th.EW_selt
        performane_log['NESW_selt'] = th.NESW_selt
        performane_log['HG_selt'] = th.HG_selt
        performane_log['HG_selt'] = th.HG_selt

        performane_log['dead_GS_count'] = cov.dead_GS_count
        performane_log['GS_coverage_metric'] = cov.GS_coverage_metric
        performane_log['dead_flight_count'] = cov.dead_flight_count
        performane_log['flight_coverage_metric'] = cov.flight_coverage_metric

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
