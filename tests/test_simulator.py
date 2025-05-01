'''
This module contains unit tests for the LEO constellation and aviation constellation simulators.
The tests verify the functionality of single-shell and multi-shell simulations in both serial and parallel modes.
Summary of tests:
1. `test_leo_con_simulator_single_shell`: Tests the LEO constellation simulator with a single shell in both serial and parallel modes.
2. `test_leo_con_simulator_multi_shell`: Tests the LEO constellation simulator with multiple shells in both serial and parallel modes.
3. `test_leo_aviation_con_simulator_single_shell`: Tests the LEO aviation constellation simulator with a single shell in both serial and parallel modes.
4. `test_leo_aviation_con_simulator_multi_shell`: Tests the LEO aviation constellation simulator with multiple shells in both serial and parallel modes.
'''


import os
import shutil
import unittest

from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import InternetTrafficAcrossCities, InternetTrafficOnAir
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.simulator.LEO_aviation_constellation_simulator import \
    LEOAviationConstellationSimulator
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from tests.test_LEO_aviation_constellation import _create_aircraft
from tests.test_LEO_constellation import _create_gs, _create_loss_model


def _create_aviation_con(log: str, multi_shell: bool = False) -> LEOAviationConstellationSimulator:
    simulator = LEOAviationConstellationSimulator(
        InternetTrafficOnAir.ONLY_POP_100_300Kbps, log
    )
    for x in [30.0, 40.0, 50.0]:
        leo_con = LEOAviationConstellation()
        leo_con.v.verbose = False
        leo_con.add_ground_stations(_create_gs())
        leo_con.add_aircrafts(_create_aircraft())
        leo_con.set_time()
        leo_con.set_loss_model(_create_loss_model())

        # Starlink Shell 1
        leo_con.add_shells(PlusGridShell(
            id=0,
            orbits=72,
            sat_per_orbit=22,
            altitude_m=550000.0,
            inclination_degree=53.0,
            angle_of_elevation_degree=25.0,
            phase_offset=x
        ))
        if multi_shell:
            leo_con.add_shells(PlusGridShell(
                id=1,
                orbits=72,
                sat_per_orbit=22,
                altitude_m=540000.0,
                inclination_degree=53.2,
                angle_of_elevation_degree=25.0,
                phase_offset=x
            ))
            leo_con.add_shells(PlusGridShell(
                id=2,
                orbits=36,
                sat_per_orbit=20,
                altitude_m=570000.0,
                inclination_degree=70.0,
                angle_of_elevation_degree=25.0,
                phase_offset=x
            ))
        simulator.add_constellation(leo_con)

    return simulator


def _create_leo_con(log: str, multi_shell: bool = False) -> LEOConstellationSimulator:
    simulator = LEOConstellationSimulator(
        InternetTrafficAcrossCities.POP_GDP_100, log
    )

    for x in [30.0, 40.0, 50.0]:
        leo_con = LEOConstellation()
        leo_con.v.verbose = False
        leo_con.add_ground_stations(_create_gs())
        leo_con.set_time()
        leo_con.set_loss_model(_create_loss_model())

        # Starlink Shell 1
        leo_con.add_shells(PlusGridShell(
            id=0,
            orbits=72,
            sat_per_orbit=22,
            altitude_m=550000.0,
            inclination_degree=53.0,
            angle_of_elevation_degree=25.0,
            phase_offset=x
        ))
        if multi_shell:
            leo_con.add_shells(PlusGridShell(
                id=1,
                orbits=72,
                sat_per_orbit=22,
                altitude_m=540000.0,
                inclination_degree=53.2,
                angle_of_elevation_degree=25.0,
                phase_offset=x
            ))
            leo_con.add_shells(PlusGridShell(
                id=2,
                orbits=36,
                sat_per_orbit=20,
                altitude_m=570000.0,
                inclination_degree=70.0,
                angle_of_elevation_degree=25.0,
                phase_offset=x
            ))
        simulator.add_constellation(leo_con)

    return simulator


class TestSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.test_directory = f'{os.getcwd()}/TestLEOSimulator'
        os.makedirs(self.test_directory, exist_ok=True)

        self.leo_con_s_csv = f'{self.test_directory}/leo_con_s.csv'
        self.leo_con_sm_csv = f'{self.test_directory}/leo_con_sm.csv'

        self.leo_con_p_csv = f'{self.test_directory}/leo_con_p.csv'
        self.leo_con_pm_csv = f'{self.test_directory}/leo_con_pm.csv'

        self.leo_con_avi_s_csv = f'{self.test_directory}/leo_con_avi_s.csv'
        self.leo_con_avi_sm_csv = f'{self.test_directory}/leo_con_avi_sm.csv'

        self.leo_con_avi_p_csv = f'{self.test_directory}/leo_con_avi_p.csv'
        self.leo_con_avi_pm_csv = f'{self.test_directory}/leo_con_avi_pm.csv'

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def test_leo_con_simulator_single_shell(self):
        print()
        s = _create_leo_con(self.leo_con_s_csv)
        s.simulate_in_serial()
        self.assertTrue(os.path.exists(self.leo_con_s_csv))

        p = _create_leo_con(self.leo_con_p_csv)
        p.simulate_in_parallel()
        self.assertTrue(os.path.exists(self.leo_con_p_csv))

    def test_leo_con_simulator_multi_shell(self):
        print()
        sm = _create_leo_con(self.leo_con_sm_csv, True)
        sm.simulate_in_serial()
        self.assertTrue(os.path.exists(self.leo_con_sm_csv))

        pm = _create_leo_con(self.leo_con_pm_csv, True)
        pm.simulate_in_parallel()
        self.assertTrue(os.path.exists(self.leo_con_pm_csv))

    def test_leo_aviation_con_simulator_single_shell(self):
        print()
        s = _create_aviation_con(self.leo_con_avi_s_csv)
        s.simulate_in_serial()
        self.assertTrue(os.path.exists(self.leo_con_avi_s_csv))

        p = _create_leo_con(self.leo_con_avi_p_csv)
        p.simulate_in_parallel()
        self.assertTrue(os.path.exists(self.leo_con_avi_p_csv))

    def test_leo_aviation_con_simulator_multi_shell(self):
        print()
        sm = _create_leo_con(self.leo_con_avi_sm_csv, True)
        sm.simulate_in_serial()
        self.assertTrue(os.path.exists(self.leo_con_avi_sm_csv))

        pm = _create_leo_con(self.leo_con_pm_csv, True)
        pm.simulate_in_parallel()
        self.assertTrue(os.path.exists(self.leo_con_pm_csv))
