import json
import os
import shutil
import unittest

from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.performance.aviation.coverage import Coverage
from LEOCraft.performance.aviation.stretch import Stretch
from LEOCraft.performance.aviation.throughput import Throughput
from LEOCraft.user_terminals.aircraft import Aircraft
from tests.test_LEO_constellation import (_create_gs, _create_loss_model,
                                          _starlink_shell_1, _starlink_shell_2,
                                          _starlink_shell_3)


def _create_aircraft() -> Aircraft:
    return Aircraft(
        replaced_gs_csv='dataset/aircraft/flightReplacedGS.csv',
        flight_cluster_csv='dataset/aircraft/flightCluster.csv'
    )


def _create_single_shell(parallel_mode: bool = True) -> LEOAviationConstellation:
    print()
    leo_con = LEOAviationConstellation(
        'SingleShellTest', PARALLEL_MODE=parallel_mode
    )
    leo_con.add_ground_stations(_create_gs())
    leo_con.add_aircrafts(_create_aircraft())
    # Adding Shells
    leo_con.add_shells(_starlink_shell_1())
    leo_con.set_time()  # Time passed after epoch
    leo_con.set_loss_model(_create_loss_model())
    leo_con.build()
    leo_con.create_network_graph()
    leo_con.generate_routes()
    print()
    return leo_con


def _create_multi_shell(parallel_mode: bool = True) -> LEOAviationConstellation:
    print()
    leo_con = LEOAviationConstellation(
        'SingleMultiTest', PARALLEL_MODE=parallel_mode
    )
    leo_con.add_ground_stations(_create_gs())
    leo_con.add_aircrafts(_create_aircraft())
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


class TestLEOAviationConstellation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.test_directory = f'{os.getcwd()}/TestLEOAviationConstellation'
        os.makedirs(self.test_directory, exist_ok=True)

        self.sshell_1 = _create_single_shell()
        self.sshell_3 = _create_multi_shell()

        self.pshell_1 = _create_single_shell(parallel_mode=False)
        self.pshell_3 = _create_multi_shell(parallel_mode=False)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def _get_throughput(self, leo_con: LEOAviationConstellation) -> float:
        th = Throughput(
            leo_con, 'dataset/air_traffic/flight_cluster_population_only_tm_100.json'
        )
        th.build()
        th.compute()
        return th.throughput_Gbps

    def _get_coverage(self, leo_con: LEOAviationConstellation) -> tuple[float, int, float, int]:
        cov = Coverage(leo_con)
        cov.build()
        cov.compute()
        return cov.GS_coverage_metric, cov.dead_GS_count, cov.flight_coverage_metric, cov.dead_flight_count

    def _get_stretch(self, leo_con: LEOAviationConstellation) -> tuple[float, float, float, float, float, float, float, float, float, float]:
        sth = Stretch(leo_con)
        sth.build()
        sth.compute()
        return sth.NS_sth, sth.NS_cnt, sth.EW_sth, sth.EW_cnt, sth.NESW_sth, sth.NESW_cnt, sth.HG_sth, sth.HG_cnt, sth.LG_sth, sth.LG_cnt

    def _read_json(self, path: str) -> dict:
        with open(path) as json_file:
            return json.loads(json_file.read())

    def _read_lines(self, path: str) -> int:
        with open(path) as file:
            return len(file.read().strip().split('\n'))

    def _test_files(self, leo_con: LEOAviationConstellation):
        path = leo_con.export_gsls(self.test_directory)
        content = self._read_json(path)
        self.assertEqual(len(leo_con.gsls), len(content.keys()))
        for k, v in content.items():
            id = leo_con.ground_stations.decode_name(k)
            for sat_name, dist_m in v:
                self.assertTrue((sat_name, dist_m) in leo_con.gsls[id])

        path = leo_con.export_fsls(self.test_directory)
        content = self._read_json(path)
        self.assertEqual(len(leo_con.fsls), len(content.keys()))
        for k, v in content.items():
            id = leo_con.aircrafts.decode_name(k)
            for sat_name, dist_m in v:
                self.assertTrue((sat_name, dist_m) in leo_con.fsls[id])

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
        self._test_files(self.pshell_1)
        self._test_files(self.pshell_3)

    def test_routes(self):
        self.assertDictEqual(self.pshell_1.routes, self.sshell_1.routes)
        self.assertDictEqual(self.pshell_3.routes, self.sshell_3.routes)

    def test_gsls(self):
        for gid, gsls in enumerate(self.sshell_1.gsls):
            self.assertSetEqual(self.pshell_1.gsls[gid], gsls)
        for gid, gsls in enumerate(self.sshell_3.gsls):
            self.assertSetEqual(self.pshell_3.gsls[gid], gsls)

    def test_fsls(self):
        for fid, fsls in enumerate(self.sshell_1.fsls):
            self.assertSetEqual(self.pshell_1.fsls[fid], fsls)
        for fid, fsls in enumerate(self.sshell_3.fsls):
            self.assertSetEqual(self.pshell_3.fsls[fid], fsls)

    def test_throughput(self):
        self.assertEqual(
            self._get_throughput(self.sshell_1),
            self._get_throughput(self.pshell_1)
        )
        self.assertEqual(
            self._get_throughput(self.sshell_3),
            self._get_throughput(self.pshell_3)
        )

    def test_stretch(self):
        self.assertTupleEqual(
            self._get_stretch(self.sshell_1),
            self._get_stretch(self.pshell_1)
        )
        self.assertTupleEqual(
            self._get_stretch(self.sshell_3),
            self._get_stretch(self.pshell_3)
        )

    def test_coverage(self):
        self.assertTupleEqual(
            self._get_coverage(self.sshell_1),
            self._get_coverage(self.pshell_1)
        )
        self.assertTupleEqual(
            self._get_coverage(self.sshell_3),
            self._get_coverage(self.pshell_3)
        )
