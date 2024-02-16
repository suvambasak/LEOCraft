import os
import shutil
import unittest

from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.terminal import TerminalCoordinates


class TestPlusGridShell(unittest.TestCase):

    def read_file(self, path: str) -> str:
        with open(path) as _file:
            return _file.read().strip()

    def valid_sat_count(self, file_content: str, sat_count: int) -> bool:
        return len(file_content.split('\n'))/3 == sat_count

    def valid_isl_count(self, file_content: str, isl_count: int) -> bool:
        return len(file_content.split('\n'))-1 == isl_count

    @classmethod
    def setUpClass(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.test_directory = f'{os.getcwd()}/TestPlusGridShell'
        os.makedirs(self.test_directory, exist_ok=True)

        self.small_shell = PlusGridShell(
            id=0,
            orbits=10,
            sat_per_orbit=10,
            altitude_m=2000000.0,
            inclination_degree=90.0,
            angle_of_elevation_degree=30.0,
            phase_offset=50.0
        )
        self.small_shell.build_satellites()
        self.small_shell.build_ISLs()

        self.big_shell = PlusGridShell(
            id=0,
            orbits=30,
            sat_per_orbit=30,
            altitude_m=550000.0,
            inclination_degree=50.0,
            angle_of_elevation_degree=25.0,
            phase_offset=10.0,
        )
        self.big_shell.build_satellites()
        self.big_shell.build_ISLs()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def test_invalid_input(self):
        for p in [-10.0, 55.0]:
            with self.assertRaises(ValueError):
                PlusGridShell(
                    id=0,
                    orbits=30,
                    sat_per_orbit=30,
                    altitude_m=550000.0,
                    inclination_degree=50.0,
                    angle_of_elevation_degree=25.0,
                    phase_offset=p
                )

    def test_export_satellites(self):
        filename = self.small_shell.export_satellites(self.test_directory)
        self.assertTrue(
            self.valid_sat_count(
                self.read_file(filename),
                self.small_shell.sat_per_orbit*self.small_shell.orbits
            )
        )

        filename = self.big_shell.export_satellites(self.test_directory)
        self.assertTrue(
            self.valid_sat_count(
                self.read_file(filename),
                self.big_shell.sat_per_orbit*self.big_shell.orbits
            )
        )

    def test_export_isls(self):
        filename = self.small_shell.export_isls(self.test_directory)
        self.assertTrue(
            self.valid_isl_count(
                self.read_file(filename),
                self.small_shell.sat_per_orbit*self.small_shell.orbits*2
            )
        )

        filename = self.big_shell.export_isls(self.test_directory)
        self.assertTrue(
            self.valid_isl_count(
                self.read_file(filename),
                self.big_shell.sat_per_orbit*self.big_shell.orbits*2
            )
        )

    def test_distance_between_sat_m(self):
        self.assertGreater(
            self.small_shell.distance_between_sat_m(0, 2)[0],
            self.small_shell.distance_between_sat_m(0, 1)[0]
        )
        self.assertGreater(
            self.small_shell.distance_between_sat_m(0, 10)[0],
            self.small_shell.distance_between_sat_m(5, 15)[0]
        )

        self.assertGreater(
            self.big_shell.distance_between_sat_m(0, 2)[0],
            self.big_shell.distance_between_sat_m(0, 1)[0]
        )
        self.assertAlmostEqual(
            self.big_shell.distance_between_sat_m(0, 10)[0],
            self.big_shell.distance_between_sat_m(5, 15)[0],
            delta=1
        )

    def test_get_satellites_in_range(self):
        _tc = TerminalCoordinates(
            name='test',
            latitude_degree='0.0',
            longitude_degree='0.0',
            elevation_m=0,
            cartesian_x=0.0,
            cartesian_y=0.0,
            cartesian_z=0.0
        )

        _, visible_sats_s, sats_range_m_s = self.small_shell.get_satellites_in_range(
            _tc
        )
        _, visible_sats_b, sats_range_m_b = self.big_shell.get_satellites_in_range(
            _tc
        )

        self.assertGreater(
            sum(sats_range_m_s)/len(sats_range_m_s),
            sum(sats_range_m_b)/len(sats_range_m_b)
        )
        self.assertGreater(len(visible_sats_b), len(visible_sats_s))
