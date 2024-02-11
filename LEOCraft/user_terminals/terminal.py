import csv
import math
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from geopy.distance import great_circle


@dataclass
class TerminalCoordinates:
    '''Stores the name and coordinates of a user terminal eg: latitude, longitude, elevation, and (x, y, z)'''

    name: str

    latitude_degree: str
    longitude_degree: str

    elevation_m: float

    cartesian_x: float
    cartesian_y: float
    cartesian_z: float


class UserTerminal(ABC):

    def __init__(self) -> None:
        self.terminals: list[TerminalCoordinates] = list()

    @abstractmethod
    def build(self) -> None:
        "Creates Terminal Coordinates object for each user terminal"
        pass

    @abstractmethod
    def encode_name(self, id: int) -> str:
        '''Encode ground station name

        Parameters
        -------
        gid: int
            Terminal ID

        Returns
        -------
        str
            Encode terminal name
        '''
        pass

    @abstractmethod
    def decode_name(self, name: str) -> int:
        """Decode ground station name

        Parameters
        -------
        name: str
            Encoded name

        Returns
        -------
        int
            id
        """
        pass

    def export(self, prefix_path: str = '.') -> str:
        """Write ground station terminal coordinates into a  CSV file at given path (default current directory)

        Parameters
        ----------
        prefix_path: str, optional
            File directory

        Returns
        -------
        str
            File name 
        """

        filename = f'{
            prefix_path}/{self.__class__.__name__}_{len(self.terminals)}.csv'

        # Convert to dict list
        data = [asdict(terminal) for terminal in self.terminals]

        # Write CSV file
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return filename

    @staticmethod
    def geodetic_to_cartesian(lat_degree: float, long_degree: float, elevation_m: float) -> tuple[float, float, float]:
        """Compute geodetic coordinates (latitude, longitude, elevation) to Cartesian coordinates (x, y, z).

        Parameters
        ----------
        lat_degree : float
            Latitude in degree
        long_degree: float
            Longitude in degrees
        elevation_m: float
            Elevation in meter

        Returns
        -------
        tuple[float, float, float]
            Cartesian coordinate as 3-tuple of (x, y, z)

        Reference:
        [1] https://github.com/snkas/hypatia/tree/master/satgenpy
        """

        #
        # Adapted from: https://github.com/andykee/pygeodesy/blob/master/pygeodesy/transform.py
        #

        # WGS72 value,
        # Source: https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
        EARTH_RADIUS_M = 6378135.0

        # Ellipsoid flattening factor; WGS72 value
        # Taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
        f = 1.0 / 298.26

        # First numerical eccentricity of ellipsoid
        e = math.sqrt(2.0 * f - f * f)
        lat = lat_degree * (math.pi / 180.0)
        lon = long_degree * (math.pi / 180.0)

        # Radius of curvature in the prime vertical of the surface of the geodetic ellipsoid
        v = EARTH_RADIUS_M / \
            math.sqrt(1.0 - e * e * math.sin(lat) * math.sin(lat))

        x = (v + elevation_m) * math.cos(lat) * math.cos(lon)
        y = (v + elevation_m) * math.cos(lat) * math.sin(lon)
        z = (v * (1.0 - e * e) + elevation_m) * math.sin(lat)

        return x, y, z

    @staticmethod
    def geodesic_distance_between_terminals_m(terminal_1: TerminalCoordinates, terminal_2: TerminalCoordinates) -> float:
        """Compute geodetic distance in meters between two user terminals.

        Parameters
        ----------
        terminal_1: TerminalCoordinates
            TerminalCoordinates object
        terminal_2: TerminalCoordinates
            TerminalCoordinates object

        Returns
        -------
        float
            Distance in meters

        Reference:
        [1] https://github.com/snkas/hypatia/tree/master/satgenpy
        """

        # WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
        earth_radius_km = 6378.135  # 6378135.0 meters

        return great_circle(
            (float(terminal_1.latitude_degree),
             float(terminal_1.longitude_degree)),
            (float(terminal_2.latitude_degree),
             float(terminal_2.longitude_degree)),
            radius=earth_radius_km
        ).m
