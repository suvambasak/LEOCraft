import unittest
import os
import shutil
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell


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
            orbits=10,
            sat_per_orbit=10,
            altitude_m=2000000.0,
            inclination_degree=90.0,
            angle_of_elevation_degree=30.0,
            phase_offset=50.0,
            name="small_shell"
        )
        self.small_shell.build_satellites()
        self.small_shell.build_ISLs()

        self.big_shell = PlusGridShell(
            orbits=30,
            sat_per_orbit=30,
            altitude_m=550000.0,
            inclination_degree=50.0,
            angle_of_elevation_degree=25.0,
            phase_offset=10.0,
            name="big_shell"
        )
        self.big_shell.build_satellites()
        self.big_shell.build_ISLs()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

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
