import csv
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

import ephem
from astropy import units as u
from astropy.time import TimeDelta

from LEOCraft.satellite_topology.satellite import LEOSatellite
from LEOCraft.user_terminals.terminal import TerminalCoordinates, UserTerminal


@dataclass
class SatelliteInfo:
    'Satellite info for data exchange'

    id: int
    shell_id: int

    nadir_latitude_deg: float
    nadir_longitude_deg: float
    elevation_m: float

    orbit_num: int
    sat_num: int

    altitude_km: float

    # ECEF: Earth-centered, Earth-fixed coordinates, also known as geocentric coordinates
    cartesian_x: float
    cartesian_y: float
    cartesian_z: float

    nadir_x: float
    nadir_y: float
    nadir_z: float


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

    @abstractmethod
    def build_satellites(self) -> None:
        "Build TLEs and set epoch time satellites of this shell"
        pass

    @property
    @abstractmethod
    def filename(self) -> str:
        """Generates file name from orbital parameters

        Returns
        -------
        str
            File name 
        """
        # return f'{self.__class__.__name__}_{self.id}_o{self.orbits}n{self.sat_per_orbit}h{self.altitude_m}i{self.inclination_degree}e{self.angle_of_elevation_degree}p{self.phase_offset}'
        pass

    def cartesian_coordinates_of_sat(
            self, sid: int, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
    ) -> tuple[float, float, float]:
        """Convert from satellites TLE to cartesian coordinates (x, y, z) system respect to lat: 0, long: 0, elevation: 0

        Parameters
        ----------
        sid: int
            Satellite ID
        time_delta : float, optional
            Time passed from the epoch

        Returns
        -------
        tuple[float, float, float]
            cartesian coordinates (x, y, z)
        """

        _satellite = self.satellites[sid].get_satellite()

        # Set an observer location and date/time
        _observer = ephem.Observer()
        _observer.lat = '0'   # Equator
        _observer.lon = '0'   # Prime meridian
        _observer.elevation = 0

        _observer.epoch = str(self.universal_epoch)
        _observer.date = str(self.universal_epoch+time_delta)

        # Compute the satellite position
        _satellite.compute(_observer)

        # Get the x, y, z coordinates
        r = _satellite.range  # Distance to satellite in meters
        alt = _satellite.alt  # Altitude in radians
        az = _satellite.az    # Azimuth in radians

        # Convert spherical coordinates (range, altitude, azimuth) to Cartesian coordinates (x, y, z)
        x = r * math.cos(alt) * math.cos(az)
        y = r * math.cos(alt) * math.sin(az)
        z = r * math.sin(alt)

        return x, y, z

    def euclidean_distance_between_sat_m(
            self, sid_a: int, sid_b: int, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
    ) -> tuple[float, bool]:
        """Calculates euclidean distance (x, y, z) between two satellite in meters and checks the range of the ISL

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
            (Distance in meters, if satellites in ISL range)
        """

        # Get the positions of both satellites
        sat_a_x, sat_a_y, sat_a_z = self.cartesian_coordinates_of_sat(
            sid_a, time_delta)
        sat_b_x, sat_b_y, sat_b_z = self.cartesian_coordinates_of_sat(
            sid_b, time_delta)

        # Calculate the Euclidean distance between the two satellites
        distance_m = math.sqrt((sat_a_x - sat_b_x)**2 +
                               (sat_a_y - sat_b_y) ** 2 + (sat_a_z - sat_b_z)**2)

        in_ISL_range = self.satellites[sid_a].max_ISL_length_m(
        ) >= distance_m and self.satellites[sid_b].max_ISL_length_m() >= distance_m

        return distance_m, in_ISL_range

    def distance_between_sat_m(
        self,
        sid_a: int, sid_b: int, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
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
            (Distance in meters, if satellites in ISL range)
        """

        # Create an observer somewhere on the planet
        observer = ephem.Observer()
        observer.epoch = str(self.universal_epoch)
        observer.date = str(self.universal_epoch+time_delta)
        observer.lat = '0'
        observer.lon = '0'
        # lat, long = self.satellites[sid_a].nadir()
        # observer.lat, observer.lon = str(lat), str(long)
        observer.elevation = 0

        # Calculate the relative location of the satellites to this observer
        _satellite_a = self.satellites[sid_a].get_satellite()
        _satellite_b = self.satellites[sid_b].get_satellite()

        _satellite_a.compute(observer)
        _satellite_b.compute(observer)

        # print('_satellite_a', round(_satellite_a.range/1000, 1), 'km')
        # print('_satellite_b', round(_satellite_b.range/1000, 1), 'km')

        # Calculate the angle observed by the observer to the satellites (this is done because the .compute() calls earlier)
        angle_radians = float(
            repr(ephem.separation(_satellite_a, _satellite_b))
        )
        # print('Angle C:', math.degrees(angle_radians))

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

    def distance_between_terminal_sat_m(
            self, terminal: TerminalCoordinates, sat: LEOSatellite, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
    ) -> float:
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

    def get_satellites_in_range(
            self, terminal: TerminalCoordinates, tid: int = -1, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)
    ) -> tuple[int, list[str], list[float]]:
        """Generates list of satellites of this shell in the range of given user terminal 

        Parameters
        ------
        terminal: TerminalCoordinates
            User terminal coordinates
        tid: int = -1, optional,
            Terminal ID (default -1)
        time_delta: TimeDelta, optional
            Time passed from epoch. Default value: TimeDelta(0.0 * u.nanosecond)

        Returns
        -------
        tuple[int, list[str], list[float]]
            User terminal ID (if given), List of satellite names, List of corresponding distance in meters
        """

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

    def _get_orbit_num(self, sid: int) -> int:
        """Calculates orbit number from sid

        Parameters
        ------
        sid: int
            Satellite ID

        Returns
        ------
        int
            Orbit number
        """

        if sid:
            return sid//self.sat_per_orbit
        else:
            return 0

    def _get_sat_num_in_orbit(self, sid: int) -> int:
        """Calculates satellite number in orbit from sid

        Parameters
        ------
        sid: int
            Satellite ID

        Returns
        ------
        int
            Satellite number in that orbit
        """

        return sid % self.sat_per_orbit

    def build_sat_info(self, sid: int, time_delta: TimeDelta = TimeDelta(0.0 * u.nanosecond)) -> SatelliteInfo:
        """Build a dataclass object of a satellite of this shell with all the details

        Parameters
        ----------
        sid: int
            Satellite ID
        time_delta: TimeDelta, optional
            Time passed from epoch. Default value: TimeDelta(0.0 * u.nanosecond)

        Returns
        -------
        SatelliteInfo
            Satellite details
        """

        latitude, longitude, elevation_m = self.satellites[sid].nadir(
            time_delta)

        # Nadir altitude comes with few km of error
        # So updated with actual altitude input paramater
        elevation_m = self.satellites[sid].altitude_m

        # x, y, z = self.cartesian_coordinates_of_sat(sid, time_delta)
        sx, sy, sz = UserTerminal.geodetic_to_cartesian(
            latitude, longitude, elevation_m
        )
        nx, ny, nz = UserTerminal.geodetic_to_cartesian(
            latitude, longitude, 0
        )

        return SatelliteInfo(
            id=sid,
            shell_id=self.id,

            nadir_latitude_deg=latitude,
            nadir_longitude_deg=longitude,
            elevation_m=elevation_m,

            sat_num=self._get_sat_num_in_orbit(sid),
            orbit_num=self._get_orbit_num(sid),

            altitude_km=round(elevation_m/1000, 2),

            cartesian_x=sx,
            cartesian_y=sy,
            cartesian_z=sz,

            nadir_x=nx,
            nadir_y=ny,
            nadir_z=nz,
        )

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
