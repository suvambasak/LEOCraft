import csv
import math
from dataclasses import asdict

from LEOCraft.user_terminals.terminal_coordinates import TerminalCoordinates


class GroundStation:

    def __init__(self, csv_file: str) -> None:
        self.csv_file = csv_file

        self.terminals: list[TerminalCoordinates] = list()

    def build(self) -> None:
        "Creates Terminal Coordinates object for each ground stations"

        # Reading the CSV file
        with open(self.csv_file) as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Creating TerminalCoordinates objects for each GS
            for row in csv_reader:

                cartesian = self.geodetic_to_cartesian(
                    float(row["latitude_degree"]),
                    float(row["longitude_degree"]),
                    float(row["elevation_m"])
                )

                self.terminals.append(
                    TerminalCoordinates(
                        name=row['name'],
                        latitude_degree=str(row['latitude_degree']),
                        longitude_degree=str(row['longitude_degree']),
                        elevation_m=float(row['elevation_m']),
                        cartesian_x=cartesian[0],
                        cartesian_y=cartesian[1],
                        cartesian_z=cartesian[2]
                    )
                )

    def encode_GS_name(self, id: int) -> str:
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
        return f'G-{id}'

    def decode_GS_name(self, name: str) -> int:
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
        return int(name.split('-')[1])

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
