import math

import ephem
from astropy import units as u
from astropy.time import Time, TimeDelta


class LEOSatellite:
    """
    A LEO satellite class 

    - Generates TLE of a satellite
    - Computes
        - Satellite nadir at given time (satellite propagation)
        - orbital period
        - Coverage cone on Earth surface
        - Maximum range of ground to satellite, inter satellite links


    Reference:
    [1] https://github.com/snkas/hypatia/tree/master/satgenpy
    [2] Kassing S, Bhattacherjee D, Águas AB, Saethre JE, Singla A. Exploring the" Internet from space" with Hypatia. InProceedings of the ACM Internet Measurement conference 2020 Oct 27 (pp. 214-229).
    """

    # Constant for Earth
    EARTH_RADIUS_M: float = 6378135.0
    G: float = 6.67408 * 10**(-11)
    MASS: float = 5.9722*(10**24)

    # Circular orbit
    ECCENTRICITY: float = 0.0000001
    ARG_OF_PERIGEE_DEGREE: float = 0.0

    def __init__(
        self,
        altitude_m: float,
        inclination_degree: float,
        angle_of_elevation_degree: float,

        satellite_catalog_number: int,
        raan_degree: float,
        mean_anomaly_degree: float,
        satellite_name: str = 'LEOSAT'
    ) -> None:
        """Create a new satellites object

        Parameters
        ----------
        altitude_m : float
            Satellite altitude in meter(s)
        inclination_degree : float
            Angle of inclination in degree
        angle_of_elevation_degree: float
            Min angle of elevation in degree
        satellite_catalog_number: int
            Unique ID for satellite
        raan_degree: float
            Right Ascension of the Ascending Node (RAAN) in degree
        mean_anomaly_degree: float
            Mean anomaly in degree
        satellite_name: str
            Name of the container shell
        """

        assert satellite_catalog_number > 0
        assert len(satellite_name) > 0

        if altitude_m < 300000.0 or altitude_m > 2000000.0:
            raise ValueError(
                "[Required] 300.0 KM <= altitude_m <= 2000.0 KM"
            )
        if inclination_degree < 5.0 or inclination_degree > 175.0:
            raise ValueError(
                "[Required] 5.0 <= inclination_degree <= 175.0"
            )
        if angle_of_elevation_degree < 5.0 or angle_of_elevation_degree > 90.0:
            raise ValueError(
                "[Required] 5.0 <= angle_of_elevation_degree <= 90.0"
            )
        if raan_degree < 0.0 or raan_degree > 360.0:
            raise ValueError(
                "[Required] 0.0 <= raan_degree <= 360.0"
            )
        if mean_anomaly_degree < 0.0 or mean_anomaly_degree > 360.0:
            raise ValueError(
                "[Required] 0.0 <= mean_anomaly_degree <= 360.0"
            )

        self.altitude_m = float(altitude_m)
        self.inclination_degree = float(inclination_degree)
        self.angle_of_elevation_e_degree = float(angle_of_elevation_degree)

        self.satellite_catalog_number = satellite_catalog_number
        self.raan_degree = raan_degree
        self.mean_anomaly_degree = mean_anomaly_degree
        self.satellite_name = satellite_name

        self.MEAN_MOTION_REV_PER_DAY = (24*60*60)/self.orbital_period_s()

        # TLE
        self.tle_line_1: str
        self.tle_line_2: str
        self.title_line: str

    def build(self) -> None:
        "Create TLE of the satellite and epoch"

        self._build_TLE()
        self.satellite = ephem.readtle(
            self.title_line,
            self.tle_line_1,
            self.tle_line_2
        )
        epoch_year = self.tle_line_1[18:20]
        epoch_day = float(self.tle_line_1[20:32])
        self.epoch = Time("20" + epoch_year + "-01-01 00:00:00",
                          scale="tdb") + (epoch_day - 1) * u.day

    def nadir(
        self,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        nanosecond: int = 0
    ) -> tuple[float, float]:
        """Calculates satellite shadow/nadir (latitude, longitude) 
        At given time (default 0) all time unit added

        Parameters
        ----------
        day : int, optional
        hour: int, optional
        minute: int, optional
        second: int, optional
        millisecond: int, optional
        nanosecond: int, optional


        Returns
        -------
        tuple[float, float]
            (latitude, longitude) 
        """
        time_delta = TimeDelta(nanosecond * u.nanosecond)
        time_delta += TimeDelta(millisecond * u.millisecond)
        time_delta += TimeDelta(second * u.second)
        time_delta += TimeDelta(minute * u.minute)
        time_delta += TimeDelta(hour * u.hour)
        time_delta += TimeDelta(day * u.day)

        self.satellite.compute(
            str(self.epoch+time_delta),
            epoch=str(self.epoch)
        )
        return math.degrees(self.satellite.sublat), math.degrees(self.satellite.sublong)

    def _build_TLE(self) -> None:
        'Create TLE three line'

        # Epoch is 2000-01-01 00:00:00, which is 00001 in ddyyy format
        # See also: https://www.celestrak.com/columns/v04n03/#FAQ04
        self.tle_line_1 = "1 %05dU 00000ABC 00001.00000000  .00000000  00000-0  00000+0 0    0" % (
            self.satellite_catalog_number
        )

        self.tle_line_2 = "2 %05d %s %s %s %s %s %s    0" % (
            self.satellite_catalog_number,
            ("%3.4f" % self.inclination_degree).rjust(8),
            ("%3.4f" % self.raan_degree).rjust(8),
            ("%0.7f" % self.ECCENTRICITY)[2:],
            ("%3.4f" % self.ARG_OF_PERIGEE_DEGREE).rjust(8),
            ("%3.4f" % self.mean_anomaly_degree).rjust(8),
            ("%2.8f" % self.MEAN_MOTION_REV_PER_DAY).rjust(11),
        )

        # Append checksums
        self.tle_line_1 = self.tle_line_1 + \
            str(self._calculate_tle_line_checksum(self.tle_line_1))
        self.tle_line_2 = self.tle_line_2 + \
            str(self._calculate_tle_line_checksum(self.tle_line_2))
        self.title_line = self.satellite_name + " " + \
            str(self.satellite_catalog_number-1)

    def _calculate_tle_line_checksum(self, tle_line_without_checksum: str) -> int:
        if len(tle_line_without_checksum) != 68:
            raise ValueError("Must have exactly 68 characters")
        s = 0
        for i in range(len(tle_line_without_checksum)):
            if tle_line_without_checksum[i].isnumeric():
                s += int(tle_line_without_checksum[i])
            if tle_line_without_checksum[i] == "-":
                s += 1
        return s % 10

    def get_TLE(self) -> str:
        """Get the TLE of the satellite

        Returns
        -------
        str
            SAT_NAME CATALOG_NUM
            1 00002U 00000ABC 00001.00000000  .00000000  00000-0  00000+0 0    05
            2 00002  90.0000   0.0000 0000001   0.0000  36.0000 15.21916082    08
        """
        return f'{self.title_line}\n{self.tle_line_1}\n{self.tle_line_2}'

    def coverage_cone_radius_m_on_earth(self) -> float:
        """Calculates satellites coverage cone radius on Earth surface
        Returns
        -------
        float
            radius in meter(s)
        """

        return self.altitude_m / math.tan(math.radians(self.angle_of_elevation_e_degree))

    def orbital_period_s(self) -> float:
        """Calculates orbital period of the satellite in seconds
        Returns
        -------
        float
            second(s)
        """

        orbit_radius = self.EARTH_RADIUS_M + self.altitude_m
        return math.sqrt(
            (4 * (math.pi**2) * orbit_radius**3)/(self.G * self.MASS)
        )

    def max_GSL_length_m(self) -> float:
        """Calculates maximum possible GSL length"

        Returns
        -------
        float
            length in meter(s)
        """

        _coverage_cone_radius_m_on_earth = self.coverage_cone_radius_m_on_earth()
        return math.sqrt(
            math.pow(_coverage_cone_radius_m_on_earth, 2) +
            math.pow(self.altitude_m, 2)
        )

    def max_ISL_length_m(self) -> float:
        """Calculates maximum possible ISL length(m) which is upto 80km above Earth surface

        Returns
        -------
        float
            length in meter(s)
        """
        return 2 * math.sqrt(
            math.pow(self.EARTH_RADIUS_M + self.altitude_m, 2) -
            math.pow(self.EARTH_RADIUS_M + 80000, 2)
        )
