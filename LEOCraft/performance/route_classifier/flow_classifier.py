import math
from abc import ABC, abstractmethod

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.user_terminals.terminal import TerminalCoordinates


class FlowClassifier(ABC):
    '''Create categories based on the based on the orientation of the end to end traffic flow

    Computer the slope and distance between two user terminal and create classes like:
    - North south routes
    - East west routes
    - NorthEast SouthWest routes
    - High geodesic distance routes
    - Low geodesic distance routes
    '''

    _HIGH_GEODESIC_BOUND_M = 8000 * 1000
    _LOW_GEODESIC_BOUND_M = 2000 * 1000
    _EAST_WEST_BOUND_DEGREE = 15
    _NORTH_SOUTH_BOUND_DEGREE = 75

    route_north_south: set[str]
    route_east_west: set[str]
    route_northeast_southwest: set[str]

    route_high_geodesic: set[str]
    route_low_geodesic: set[str]

    def __init__(self, leo_con: Constellation | LEOConstellation | LEOAviationConstellation) -> None:
        self.leo_con = leo_con

        self.route_north_south = set()
        self.route_east_west = set()
        self.route_northeast_southwest = set()

        self.route_high_geodesic = set()
        self.route_low_geodesic = set()

    @abstractmethod
    def classify(self) -> None:
        'Classify the routes based on orientation'
        pass

    def calculate_slope(self, terminal_s: TerminalCoordinates, terminal_d: TerminalCoordinates) -> tuple[float, float]:
        '''Encode ground station name

        Parameters
        -------
        terminal_s: TerminalCoordinates
            Source TerminalCoordinates
        terminal_d: TerminalCoordinates
            Destination TerminalCoordinates


        Returns
        -------
        tuple[float, float]
            Slope amd slope in degrees
        '''

        slope = (float(terminal_d.latitude_degree) - float(terminal_s.latitude_degree)) / \
            (float(terminal_d.longitude_degree) -
             float(terminal_s.longitude_degree))
        slope_in_degrees = math.degrees(math.atan(slope))
        return slope, slope_in_degrees
