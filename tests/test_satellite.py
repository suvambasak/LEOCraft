import unittest

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.satellite_topology.satellite import LEOSatellite


class TestSatellite(unittest.TestCase):

    altitude_m = 500*1000
    inclination_degree = 90
    angle_of_elevation_degree = 30
    satellite_catalog_number = 1
    raan_degree = 0
    mean_anomaly_degree = 0
    satellite_name = 'Test'

    def test_invalid_input(self):

        for h in [100, 2000*1000+5]:
            with self.assertRaises(ValueError):
                LEOSatellite(
                    altitude_m=h,
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=self.satellite_catalog_number,
                    raan_degree=self.raan_degree,
                    mean_anomaly_degree=self.mean_anomaly_degree,
                    satellite_name=self.satellite_name
                )

        for i in [3, 180]:
            with self.assertRaises(ValueError):
                LEOSatellite(
                    altitude_m=self.altitude_m,
                    inclination_degree=i,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=self.satellite_catalog_number,
                    raan_degree=self.raan_degree,
                    mean_anomaly_degree=self.mean_anomaly_degree,
                    satellite_name=self.satellite_name
                )
        for e in [3, 180]:
            with self.assertRaises(ValueError):
                LEOSatellite(
                    altitude_m=self.altitude_m,
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=e,
                    satellite_catalog_number=self.satellite_catalog_number,
                    raan_degree=self.raan_degree,
                    mean_anomaly_degree=self.mean_anomaly_degree,
                    satellite_name=self.satellite_name
                )

        for x in [-10, 365]:
            with self.assertRaises(ValueError):
                LEOSatellite(
                    altitude_m=self.altitude_m,
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=self.satellite_catalog_number,
                    raan_degree=x,
                    mean_anomaly_degree=self.mean_anomaly_degree,
                    satellite_name=self.satellite_name
                )

            with self.assertRaises(ValueError):
                LEOSatellite(
                    altitude_m=self.altitude_m,
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=self.satellite_catalog_number,
                    raan_degree=self.raan_degree,
                    mean_anomaly_degree=x,
                    satellite_name=self.satellite_name
                )

            # with self.assertRaises(ValueError):
            #     LEOSatellite(
            #         altitude_m=self.altitude_m,
            #         inclination_degree=self.inclination_degree,
            #         angle_of_elevation_degree=self.angle_of_elevation_degree,
            #         satellite_catalog_number=self.satellite_catalog_number,
            #         raan_degree=self.raan_degree,
            #         mean_anomaly_degree=self.mean_anomaly_degree,
            #         satellite_name=self.satellite_name
            #     )

    def test_coverage_cone_radius_m(self):
        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m+100,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertGreater(
            leo_con_2.coverage_cone_radius_m(),
            leo_con_1.coverage_cone_radius_m()
        )

        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree+10,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertGreater(
            leo_con_2.coverage_cone_radius_m(),
            leo_con_1.coverage_cone_radius_m()
        )

        self.assertGreater(
            leo_con_1.coverage_cone_radius_m(),
            leo_con_1.coverage_cone_radius_m(10000)
        )
        self.assertGreater(
            leo_con_2.coverage_cone_radius_m(),
            leo_con_2.coverage_cone_radius_m(500)
        )

    def test_orbital_period_s(self):
        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m+1000,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertGreater(
            leo_con_2.orbital_period_s(),
            leo_con_1.orbital_period_s()
        )

        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree-10,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertEqual(
            leo_con_2.orbital_period_s(),
            leo_con_1.orbital_period_s()
        )

    def test_max_ISL_length_m(self):
        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m+1000,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertGreater(
            leo_con_2.max_ISL_length_m(),
            leo_con_1.max_ISL_length_m()
        )

    def test_max_GSL_length_m(self):
        leo_con_1 = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con_2 = LEOSatellite(
            altitude_m=self.altitude_m+10,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )

        self.assertGreater(
            leo_con_2.max_GSL_length_m(),
            leo_con_1.max_GSL_length_m()
        )

    def test_TLE(self):
        leo_con = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree,
            satellite_name=self.satellite_name
        )
        leo_con.build()
        self.assertEqual(
            leo_con.get_TLE(),
            "Test 0\n"+"1 00001U 00000ABC 00001.00000000  .00000000  00000-0  00000+0 0    04\n" +
            "2 00001  90.0000   0.0000 0000001   0.0000   0.0000 15.21916082    08"
        )

        leo_con = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number+1,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree+36,
            satellite_name=self.satellite_name
        )
        leo_con.build()
        self.assertEqual(
            leo_con.get_TLE(),
            "Test 1\n"+"1 00002U 00000ABC 00001.00000000  .00000000  00000-0  00000+0 0    05\n" +
            "2 00002  90.0000   0.0000 0000001   0.0000  36.0000 15.21916082    08"
        )

    def test_nadir(self):
        leo_con = LEOSatellite(
            altitude_m=self.altitude_m,
            inclination_degree=self.inclination_degree,
            angle_of_elevation_degree=self.angle_of_elevation_degree,
            satellite_catalog_number=self.satellite_catalog_number+1,
            raan_degree=self.raan_degree,
            mean_anomaly_degree=self.mean_anomaly_degree+36,
            satellite_name=self.satellite_name
        )
        leo_con.build()
        self.assertEqual(
            leo_con.nadir(
                Constellation.calculate_time_delta(day=1)
            ),
            leo_con.nadir(
                Constellation.calculate_time_delta(hour=24)
            )
        )
        self.assertEqual(
            leo_con.nadir(
                Constellation.calculate_time_delta(hour=1)
            ),
            leo_con.nadir(
                Constellation.calculate_time_delta(minute=60)
            )
        )
        self.assertEqual(
            leo_con.nadir(
                Constellation.calculate_time_delta(second=1)
            ),
            leo_con.nadir(
                Constellation.calculate_time_delta(millisecond=1000)
            )
        )
        self.assertEqual(
            leo_con.nadir(Constellation.calculate_time_delta(millisecond=1)),
            leo_con.nadir(
                Constellation.calculate_time_delta(nanosecond=1000000))
        )

        lat_1, _ = leo_con.nadir()
        lat_2, _ = leo_con.nadir(
            Constellation.calculate_time_delta(
                second=leo_con.orbital_period_s()
            )
        )
        self.assertAlmostEqual(lat_1, lat_2, delta=1)
