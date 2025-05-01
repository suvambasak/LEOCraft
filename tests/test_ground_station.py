'''
This module contains unit tests for the `GroundStation` class and its functionality.
It tests the following:
1. Encoding and decoding of terminal IDs to ensure consistency.
2. Calculation of geodesic distances between terminals to verify correctness.
3. Exporting terminal data to a CSV file and validating its contents.
'''

import csv
import os
import shutil
import unittest

from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.dataset import GroundStationAtCities


class TestGroundStation(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        self.test_directory = f'{os.getcwd()}/TestGroundStations'
        os.makedirs(self.test_directory, exist_ok=True)

        self.small_gs = GroundStation(GroundStationAtCities.TOP_100)
        self.small_gs.build()

        self.big_gs = GroundStation(GroundStationAtCities.TOP_1000)
        self.big_gs.build()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def test_encode_decode_name(self):
        for id in range(len(self.small_gs.terminals)):
            self.assertEqual(
                id, self.small_gs.decode_name(self.small_gs.encode_name(id))
            )
        for id in range(len(self.big_gs.terminals)):
            self.assertEqual(
                id, self.big_gs.decode_name(self.big_gs.encode_name(id))
            )

    def test_geodesic_distance(self):

        self.assertGreater(
            self.small_gs.geodesic_distance_between_terminals_m(
                self.small_gs.terminals[1],
                self.small_gs.terminals[30]
            ),
            self.small_gs.geodesic_distance_between_terminals_m(
                self.small_gs.terminals[1],
                self.small_gs.terminals[4]
            )
        )
        self.assertGreater(
            self.small_gs.geodesic_distance_between_terminals_m(
                self.small_gs.terminals[28],
                self.small_gs.terminals[37]
            ),
            self.small_gs.geodesic_distance_between_terminals_m(
                self.small_gs.terminals[28],
                self.small_gs.terminals[24]
            )
        )
        self.assertGreater(
            self.big_gs.geodesic_distance_between_terminals_m(
                self.big_gs.terminals[1],
                self.big_gs.terminals[30]
            ),
            self.big_gs.geodesic_distance_between_terminals_m(
                self.big_gs.terminals[1],
                self.big_gs.terminals[4]
            )
        )
        self.assertGreater(
            self.big_gs.geodesic_distance_between_terminals_m(
                self.big_gs.terminals[28],
                self.big_gs.terminals[37]
            ),
            self.big_gs.geodesic_distance_between_terminals_m(
                self.big_gs.terminals[28],
                self.big_gs.terminals[24]
            )
        )

    def _test_csv(self, path, gs: GroundStation) -> bool:
        records = list()

        with open(path) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                records.append(row)

        for row, g in zip(records, gs.terminals):
            self.assertEqual(row["latitude_degree"], g.latitude_degree)
            self.assertEqual(row["longitude_degree"], g.longitude_degree)
            self.assertEqual(row["elevation_m"], str(g.elevation_m))
            self.assertEqual(row["cartesian_x"], str(g.cartesian_x))
            self.assertEqual(row["cartesian_y"], str(g.cartesian_y))
            self.assertEqual(row["cartesian_z"], str(g.cartesian_z))

    def test_export(self):
        self._test_csv(
            self.small_gs.export(self.test_directory),
            self.small_gs
        )
        self._test_csv(
            self.big_gs.export(self.test_directory),
            self.small_gs
        )
