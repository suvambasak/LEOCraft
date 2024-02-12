import csv
import math
from abc import ABC, abstractmethod

import ephem
from astropy import units as u
from astropy.time import TimeDelta

from LEOCraft.satellite import LEOSatellite
from LEOCraft.user_terminals.terminal import TerminalCoordinates


class LEOSatelliteTopology(ABC):
    """
    Abstract Class for LEO satellite topology implements the functionality of a shell, act like a container of satellites for a shell.
    All inherited class would implement one ISL topology i.e., +Grid, xGrid etc.

    - Generates TLE of all the satellite in a shell
    - Export TLEs into a file
    - Export ISLs into a CSV file


    Reference:
    [1] https://github.com/snkas/hypatia/tree/master/satgenpy
    [2] Kassing S, Bhattacherjee D, Águas AB, Saethre JE, Singla A. Exploring the" Internet from space" with Hypatia. InProceedings of the ACM Internet Measurement conference 2020 Oct 27 (pp. 214-229).
    """

    def __init__(
        self,
        id: int,
        orbits: int,
        sat_per_orbit: int,

        altitude_m: float,
        inclination_degree: float,
        angle_of_elevation_degree: float,
        phase_offset: float,
    ) -> None:
        """Create a new shell for a LEO constellation

        Parameters
        ----------
        id: int
            Unique shell number
        orbits: int
            Number of orbits
        sat_per_orbit: int
            Number of satellites per orbit
        altitude_m : float
            Satellite altitude in meter(s)
        inclination_degree : float
            Angle of inclination in degree
        angle_of_elevation_degree:
            Min angle of elevation in degree

        phase_offset: float: float
            Offset between satellite of adjacent orbit
        """

        assert orbits > 9
        assert sat_per_orbit > 9
        assert id >= 0
        if phase_offset < 0.0 or phase_offset > 50.0:
            raise ValueError("[Required] 0.0 <= phase_offset <= 50.0")

        self.orbits = orbits
        self.sat_per_orbit = sat_per_orbit
        self.altitude_m = altitude_m
        self.inclination_degree = inclination_degree
        self.angle_of_elevation_degree = angle_of_elevation_degree
        self.phase_offset = round(float(phase_offset)/100, 2)

        self.id = id

        self.satellites: list[LEOSatellite] = list()
        self.isls: set[tuple[int, int]] = set()

        self.universal_epoch = None

    @abstractmethod
    def build_ISLs(self) -> None:
        "Creates ISL links (sat_1, sat_2)"
        pass

    def build_satellites(self) -> None:
        "Build TLEs and set epoch time satellites of this shell"

        satellite_counter = 0

        for orbit in range(0, self.orbits):

            # Orbit across longitude
            raan_degree = orbit * 360.0 / self.orbits
            orbit_wise_shift = 0
            if orbit % 2 == 1:
                # Phase_offset between two adjacent orbits
                orbit_wise_shift = 360.0 / self.sat_per_orbit * self.phase_offset

            # For each satellite in the orbit
            for n_sat in range(0, self.sat_per_orbit):

                # Position of the satellite in orbit
                mean_anomaly_degree = orbit_wise_shift + \
                    (n_sat * 360 / self.sat_per_orbit)

                # Creating satellites
                leosat = LEOSatellite(
                    altitude_m=self.altitude_m,
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=satellite_counter+1,
                    raan_degree=raan_degree,
                    mean_anomaly_degree=mean_anomaly_degree,
                    satellite_name=self.name
                )
                leosat.build()

                # Fetch and check the epoch from the TLES data
                # In the TLE, the epoch is given with a Julian data of yyddd.fraction
                # ddd is actually one-based, meaning e.g. 18001 is 1st of January, or 2018-01-01 00:00.
                # As such, to convert it to Astropy Time, we add (ddd - 1) days to it
                # See also: https://www.celestrak.com/columns/v04n03/#FAQ04

                # Consistent epoch check
                if self.universal_epoch is None:
                    self.universal_epoch = leosat.epoch
                if leosat.epoch != self.universal_epoch:
                    raise ValueError("The epoch of all TLES must be the same")
                self.satellites.append(leosat)

                satellite_counter += 1

    def distance_between_sat_m(
        self,
        sid_a: int, sid_b: int,

        time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
    ) -> tuple[float, bool]:
        """Calculates distance between two satellite in meters and checks the range of the ISL

        Parameters
        ----------
        sid_a: int
            Satellite ID
        sid_b: int
            Satellite ID
        time_delta : float, optional
            Time passed from the epoch

        Returns
        -------
        tuple[float, bool]
            (Diatnce in meters, if satellites in ISL range) 
        """

        # Create an observer somewhere on the planet
        observer = ephem.Observer()
        observer.epoch = str(self.universal_epoch)
        observer.date = str(self.universal_epoch+time_delta)
        observer.lat = 0
        observer.lon = 0
        observer.elevation = 0

        # Calculate the relative location of the satellites to this observer
        _satellite_a = self.satellites[sid_a].get_satellite()
        _satellite_b = self.satellites[sid_b].get_satellite()

        _satellite_a.compute(observer)
        _satellite_b.compute(observer)

        # Calculate the angle observed by the observer to the satellites (this is done because the .compute() calls earlier)
        angle_radians = float(
            repr(ephem.separation(_satellite_a, _satellite_b))
        )

        # Now we have a triangle with three knows:
        # (1) a = sat1.range (distance observer to satellite 1)
        # (2) b = sat2.range (distance observer to satellite 2)
        # (3) C = angle (the angle at the observer point within the triangle)
        #
        # Using the formula:
        # c^2 = a^2 + b^2 - 2 * a * b * cos(C)
        #
        # This gives us side c, the distance between the two satellites
        distance_m = math.sqrt(
            _satellite_a.range ** 2 + _satellite_b.range ** 2 -
            (2 * _satellite_a.range * _satellite_b.range * math.cos(angle_radians))
        )

        in_ISL_range = self.satellites[sid_a].max_ISL_length_m(
        ) >= distance_m and self.satellites[sid_b].max_ISL_length_m() >= distance_m

        return distance_m, in_ISL_range

    def distance_between_terminal_sat_m(self, terminal: TerminalCoordinates, sat: LEOSatellite, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)) -> float:
        """Computes the straight distance between a ground station and a satellite in meters

        Parameters
        -------------
        terminal: TerminalCoordinates
            Location coordinates of a user terminal
        sat: LEOSatellite
            LEO satellite
        time_delta : float, optional
            Time passed from the epoch

        Returns
        ------------
        float
            The distance between the ground station and the satellite in meters
        """

        # Create an observer on the planet where the ground station is
        observer = ephem.Observer()
        observer.epoch = str(sat.epoch)
        observer.date = str(sat.epoch+time_delta)

        # Very important: string argument is in degrees.
        # DO NOT pass a float as it is interpreted as radians
        observer.lat = str(terminal.latitude_degree)
        observer.lon = str(terminal.longitude_degree)
        observer.elevation = terminal.elevation_m

        # Compute distance from satellite to observer
        _satellite = sat.get_satellite()
        _satellite.compute(observer)

        # Return distance
        return _satellite.range

    def get_satellites_in_range(self, terminal: TerminalCoordinates, tid: int = -1, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)) -> tuple[int, list[str], list[float]]:
        visible_sats = list()
        sats_range_m = list()
        for sid, sat in enumerate(self.satellites):
            distance_m = self.distance_between_terminal_sat_m(
                terminal, sat, time_delta
            )

            # Out of range so GSL not possible
            if distance_m > sat.max_GSL_length_m(terminal.elevation_m):
                continue

            visible_sats.append(self.encode_sat_name(sid))
            sats_range_m.append(distance_m)

        return tid, visible_sats, sats_range_m

    @property
    def filename(self) -> str:
        """Generates file name from orbital parameters

        Returns
        -------
        str
            File name 
        """

        return f'{self.__class__.__name__}_{self.id}_o{self.orbits}n{self.sat_per_orbit}h{self.altitude_m}i{self.inclination_degree}e{self.angle_of_elevation_degree}p{self.phase_offset}'

    @property
    def name(self) -> str:
        """Generates shell name from shell ID

        Returns
        -------
        str
            Shell name
        """
        return f'S{self.id}'

    def encode_sat_name(self, sid: int) -> str:
        """Encodes satellite name with shell

        Parameters
        ----------
        sid: int
            Satellite ID

        Returns
        -------
        str
            Encoded satellite name with shell name
        """
        return f"{self.name}-{sid}"

    @staticmethod
    def decode_sat_name(sat_name: str) -> tuple[int, int]:
        """Decodes satellite id from shell

        Parameters
        ----------
        sat_name: str
            Encoded satellite name with shell name

        Returns
        -------
        tuple[int, int]
            Shell ID, Satellite ID
        """
        shell_info, sid = sat_name.split("-")
        return int(shell_info[1:]), int(sid)

    def export_satellites(self, prefix_path: str = '.') -> str:
        """Write satellite TLEs into a file at given path (default current directory)

        Parameters
        ----------
        prefix_path: str, optional
            File directory

        Returns
        -------
        str
            File name 
        """

        filename = f'{prefix_path}/{self.filename}.tle'
        with open(filename, 'w') as tle_file:
            for sat in self.satellites:
                tle_file.write(sat.get_TLE())
                tle_file.write('\n')

        return filename

    def export_isls(self, prefix_path: str = '.') -> str:
        """Write ISLs into a CSV file at given path (default current directory)

        Parameters
        ----------
        prefix_path: str, optional
            File directory

        Returns
        -------
        str
            File name 
        """

        filename = f'{prefix_path}/{self.filename}.isls.csv'
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(('sat_1', 'sat_2'))
            csv_writer.writerows(self.isls)

        return filename
