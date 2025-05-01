'''
This module contains unit tests for the LEOConstellation class and its related functionalities.
The tests cover the following aspects:
1. Throughput:
   - Validates the throughput computation for single-shell and multi-shell constellations.
2. Coverage:
   - Tests the ground station coverage metrics and ensures no ground stations are left uncovered.
3. Stretch:
   - Evaluates the stretch metrics (e.g., NS, EW, NESW, HG, LG) for single-shell and multi-shell constellations.
4. GSL Count:
   - Verifies the number of ground-to-satellite links (GSLs) for single-shell and multi-shell constellations.
5. Exported Files:
   - Tests the consistency of exported GSLs, routes, and path-related data with the internal state of the constellation.
6. Consistency:
   - Ensures that the results are consistent when the constellation is built with and without parallel mode.
'''


import json
import os
import shutil
import unittest

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.basic.stretch import Stretch
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation


def _starlink_shell_1() -> PlusGridShell:
    return PlusGridShell(
        id=0,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=550000.0,
        inclination_degree=53.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )


def _starlink_shell_2() -> PlusGridShell:
    return PlusGridShell(
        id=1,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=540000.0,
        inclination_degree=53.2,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )


def _starlink_shell_3() -> PlusGridShell:
    return PlusGridShell(
        id=2,
        orbits=36,
        sat_per_orbit=20,
        altitude_m=570000.0,
        inclination_degree=70.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )


def _create_loss_model() -> FSPL:
    # Pathloss model
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


def _create_gs() -> GroundStation:
    return GroundStation(GroundStationAtCities.TOP_100)


def _create_single_shell(parallel_mode: bool = True) -> LEOConstellation:
    print()
    leo_con = LEOConstellation('SingleShellTest', PARALLEL_MODE=parallel_mode)
    leo_con.add_ground_stations(_create_gs())
    # Adding Shells
    leo_con.add_shells(_starlink_shell_1())
    leo_con.set_time()  # Time passed after epoch
    leo_con.set_loss_model(_create_loss_model())
    leo_con.build()
    leo_con.create_network_graph()
    leo_con.generate_routes()
    print()
    return leo_con


def _create_multi_shell(parallel_mode: bool = True) -> LEOConstellation:
    print()
    leo_con = LEOConstellation('SingleMultiTest', PARALLEL_MODE=parallel_mode)
    leo_con.PARALLEL_MODE = parallel_mode
    leo_con.add_ground_stations(_create_gs())
    # Adding Shells
    leo_con.add_shells(_starlink_shell_1())
    leo_con.add_shells(_starlink_shell_2())
    leo_con.add_shells(_starlink_shell_3())
    leo_con.set_time()  # Time passed after epoch
    leo_con.set_loss_model(_create_loss_model())
    leo_con.build()
    leo_con.create_network_graph()
    leo_con.generate_routes()
    print()
    return leo_con


class TestLEOConstellation(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.test_directory = f'{os.getcwd()}/TestLEOConstellation'
        os.makedirs(self.test_directory, exist_ok=True)

        self.shell_1 = _create_single_shell()
        self.shell_3 = _create_multi_shell()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def _get_throughput(self, leo_con: LEOConstellation) -> float:
        th = Throughput(
            leo_con, InternetTrafficAcrossCities.POP_GDP_100
        )
        th.build()
        th.compute()
        return th.throughput_Gbps

    def _get_coverage(self, leo_con: LEOConstellation) -> tuple[float, int]:
        cov = Coverage(leo_con)
        cov.build()
        cov.compute()
        return cov.GS_coverage_metric, cov.dead_GS_count

    def _get_stretch(self, leo_con: LEOConstellation) -> tuple[
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float
    ]:
        sth = Stretch(leo_con)
        sth.build()
        sth.compute()
        return (
            sth.NS_sth,
            sth.NS_cnt,

            sth.EW_sth,
            sth.EW_cnt,

            sth.NESW_sth,
            sth.NESW_cnt,

            sth.HG_sth,
            sth.HG_cnt,

            sth.LG_sth,
            sth.LG_cnt
        )

    def test_throughput(self):
        self.assertEqual(
            round(2789.06253053825), round(self._get_throughput(self.shell_1))
        )
        self.assertEqual(
            round(5875.64403725285), round(self._get_throughput(self.shell_3))
        )

    def test_coverage(self):
        GS_coverage_metric, dead_GS_count = self._get_coverage(self.shell_1)
        self.assertEqual(round(GS_coverage_metric), round(111.844532091743))
        self.assertEqual(dead_GS_count, 0)

        GS_coverage_metric, dead_GS_count = self._get_coverage(self.shell_3)
        self.assertEqual(round(GS_coverage_metric), round(148.793946734811))
        self.assertEqual(dead_GS_count, 0)

    def test_stretch(self):
        NS_sth, NS_cnt, EW_sth, EW_cnt, NESW_sth, NESW_cnt, HG_sth, HG_cnt, LG_sth, LG_cnt = self._get_stretch(
            self.shell_1
        )
        self.assertEqual(round(1.87054240470203), round(NS_sth))
        self.assertEqual(round(1.64966164592793), round(EW_sth))
        self.assertEqual(round(1.28095163393154), round(NESW_sth))
        self.assertEqual(round(1.26115518687514), round(HG_sth))
        self.assertEqual(round(1.48617371221411), round(LG_sth))

        self.assertEqual(8, round(NS_cnt))
        self.assertEqual(8, round(EW_cnt))
        self.assertEqual(6, round(NESW_cnt))
        self.assertEqual(12, round(HG_cnt))
        self.assertEqual(4, round(LG_cnt))

        NS_sth, NS_cnt, EW_sth, EW_cnt, NESW_sth, NESW_cnt, HG_sth, HG_cnt, LG_sth, LG_cnt = self._get_stretch(
            self.shell_3
        )
        self.assertEqual(round(1.35706768827851), round(NS_sth))
        self.assertEqual(round(1.50420807825176), round(EW_sth))
        self.assertEqual(round(1.25290209130385), round(NESW_sth))
        self.assertEqual(round(1.18072439765235), round(HG_sth))
        self.assertEqual(round(1.43444620479228), round(LG_sth))

        self.assertEqual(7, round(NS_cnt))
        self.assertEqual(8, round(EW_cnt))
        self.assertEqual(6, round(NESW_cnt))
        self.assertEqual(11, round(HG_cnt))
        self.assertEqual(round(3.5), round(LG_cnt))

    def _test_gsl_count(self, leo_con: LEOConstellation):
        gsl_count = 0
        for gsl in leo_con.gsls:
            gsl_count += len(gsl)

        return gsl_count

    def test_gsl_count(self):
        self.assertEqual(self._test_gsl_count(self.shell_1), 1362)
        self.assertEqual(self._test_gsl_count(self.shell_3), 3169)

    def _read_json(self, path: str) -> dict:
        with open(path) as json_file:
            return json.loads(json_file.read())

    def _read_lines(self, path: str) -> int:
        with open(path) as file:
            return len(file.read().strip().split('\n'))

    def _test_files(self, leo_con: LEOConstellation):
        path = leo_con.export_gsls(self.test_directory)
        content = self._read_json(path)
        self.assertEqual(len(leo_con.gsls), len(content.keys()))
        for k, v in content.items():
            id = leo_con.ground_stations.decode_name(k)
            for sat_name, dist_m in v:
                self.assertTrue((sat_name, dist_m) in leo_con.gsls[id])

        path = leo_con.export_routes(self.test_directory)
        content = self._read_json(path)
        self.assertDictEqual(leo_con.routes, content)

        path = leo_con.export_no_path_found(self.test_directory)
        self.assertEqual(
            len(leo_con.no_path_found),
            self._read_lines(path)-1
        )

        path = leo_con.export_k_path_not_found(self.test_directory)
        self.assertEqual(
            len(leo_con.k_path_not_found),
            self._read_lines(path)-1
        )

    def test_exports(self):
        self._test_files(self.shell_1)
        self._test_files(self.shell_3)

    def test_consistency(self):
        _shell_1 = _create_single_shell(parallel_mode=False)
        _shell_3 = _create_multi_shell(parallel_mode=False)

        for gid, gsl in enumerate(self.shell_1.gsls):
            self.assertSetEqual(gsl, _shell_1.gsls[gid])
        for gid, gsl in enumerate(self.shell_3.gsls):
            self.assertSetEqual(gsl, _shell_3.gsls[gid])

        self.assertDictEqual(_shell_1.routes, self.shell_1.routes)
        self.assertDictEqual(_shell_3.routes, self.shell_3.routes)

        self.assertTupleEqual(
            self._get_coverage(_shell_1), self._get_coverage(self.shell_1)
        )
        self.assertTupleEqual(
            self._get_coverage(_shell_3), self._get_coverage(self.shell_3)
        )

        self.assertAlmostEqual(
            self._get_throughput(_shell_1),
            self._get_throughput(self.shell_1),
            5
        )
        self.assertAlmostEqual(
            self._get_throughput(_shell_3),
            self._get_throughput(self.shell_3),
            5
        )

        self.assertTupleEqual(
            self._get_stretch(_shell_1), self._get_stretch(self.shell_1)
        )
        self.assertTupleEqual(
            self._get_stretch(_shell_3), self._get_stretch(self.shell_3)
        )
