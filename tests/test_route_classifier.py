'''
This module tests the functionality of the `calculate_slope` method in the `AviationClassifier` and `BasicClassifier` classes. 
It ensures the method handles edge cases such as:
1. Zero denominator (vertical slope).
2. Zero numerator (horizontal slope).
3. Both numerator and denominator being zero (invalid slope).
'''


import random
import unittest

from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.performance.route_classifier.aviation_classifier import \
    AviationClassifier
from LEOCraft.performance.route_classifier.basic_classifier import \
    BasicClassifier
from LEOCraft.user_terminals.terminal import TerminalCoordinates


class TestRouteClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.class_fly = AviationClassifier(LEOAviationConstellation())
        self.class_gs = BasicClassifier(LEOConstellation())

    def _get_zero_lat(self) -> TerminalCoordinates:
        return TerminalCoordinates(
            latitude_degree=0.0,
            longitude_degree=random.random(),
            elevation_m=0.0, cartesian_x=None, cartesian_y=None, cartesian_z=None, name=''
        )

    def _get_zero_long(self) -> TerminalCoordinates:
        return TerminalCoordinates(
            latitude_degree=random.random(),
            longitude_degree=0.0,
            elevation_m=0.0, cartesian_x=None, cartesian_y=None, cartesian_z=None, name=''
        )

    def _get_zero_lat_long(self) -> TerminalCoordinates:
        return TerminalCoordinates(
            latitude_degree=0.0,
            longitude_degree=0.0,
            elevation_m=0.0, cartesian_x=None, cartesian_y=None, cartesian_z=None, name=''
        )

    def test_zero_denominator(self):
        self.assertTupleEqual(
            self.class_gs.calculate_slope(
                self._get_zero_long(), self._get_zero_long()
            ),
            (float('inf'), 90.0)
        )
        self.assertTupleEqual(
            self.class_fly.calculate_slope(
                self._get_zero_long(), self._get_zero_long()
            ),
            (float('inf'), 90.0)
        )

    def test_zero_numerator(self):
        self.assertTupleEqual(
            self.class_gs.calculate_slope(
                self._get_zero_lat(), self._get_zero_lat()
            ),
            (0.0, 0.0)
        )
        self.assertTupleEqual(
            self.class_fly.calculate_slope(
                self._get_zero_lat(), self._get_zero_lat()
            ),
            (0.0, 0.0)
        )

    def test_zero_numerator_denominator(self):
        with self.assertRaises(ValueError):
            self.class_gs.calculate_slope(
                self._get_zero_lat_long(), self._get_zero_lat_long()
            )

        with self.assertRaises(ValueError):
            self.class_fly.calculate_slope(
                self._get_zero_lat_long(), self._get_zero_lat_long()
            )
