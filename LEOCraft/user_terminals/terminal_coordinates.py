
from dataclasses import dataclass


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
