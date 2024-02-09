import math

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.user_terminals.terminal_coordinates import TerminalCoordinates


class FlowClassifier:
    '''Create categories based on the based on the orientation of the end to end traffic flow

    Computer the slope and distance between two user terminal and create classes like:
    - North south routes
    - East west routes
    - NorthEast SouthWest routes
    - High geodesic distance routes
    - Low geodesic distance routes
    '''

    __HIGH_GEODESIC_BOUND_M = 8000 * 1000
    __LOW_GEODESIC_BOUND_M = 2000 * 1000
    __EAST_WEST_BOUND_DEGREE = 15
    __NORTH_SOUTH_BOUND_DEGREE = 75

    route_north_south: set[str]
    route_east_west: set[str]
    route_northeast_southwest: set[str]

    route_high_geodesic: set[str]
    route_low_geodesic: set[str]

    def __init__(self, leo_con: Constellation) -> None:
        self.leo_con = leo_con

        self.route_north_south = set()
        self.route_east_west = set()
        self.route_northeast_southwest = set()

        self.route_high_geodesic = set()
        self.route_low_geodesic = set()

    def classify(self) -> None:
        'Classify the routes based on orientation'

        c = 0
        for sgid in range(len(self.leo_con.ground_stations.terminals)):
            for dgid in range(sgid+1, len(self.leo_con.ground_stations.terminals)):
                c += 1

                geodesic_m = GroundStation.geodesic_distance_between_terminals_m(
                    self.leo_con.ground_stations.terminals[sgid],
                    self.leo_con.ground_stations.terminals[dgid]
                )

                # High geodesic
                if geodesic_m > self.__HIGH_GEODESIC_BOUND_M:
                    self.route_high_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_GS_name(
                            sgid)}_{self.leo_con.ground_stations.encode_GS_name(dgid)}'
                    )
                    continue

                # Low geodesic
                if geodesic_m < self.__LOW_GEODESIC_BOUND_M:
                    self.route_low_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_GS_name(
                            sgid)}_{self.leo_con.ground_stations.encode_GS_name(dgid)}'
                    )
                    continue

                slope, slope_in_degrees = self.calculate_slope(
                    self.leo_con.ground_stations.terminals[sgid],
                    self.leo_con.ground_stations.terminals[dgid]
                )

                # Invalid slope
                if 90 < abs(slope_in_degrees):
                    raise ValueError(sgid, dgid, slope, slope_in_degrees)
                if 0 > abs(slope_in_degrees):
                    raise ValueError(sgid, dgid, slope, slope_in_degrees)

                # North south routes
                if self.__NORTH_SOUTH_BOUND_DEGREE < abs(slope_in_degrees):
                    self.route_north_south.add(
                        f'{self.leo_con.ground_stations.encode_GS_name(
                            sgid)}_{self.leo_con.ground_stations.encode_GS_name(dgid)}'
                    )

                # East west routes
                elif self.__EAST_WEST_BOUND_DEGREE > abs(slope_in_degrees):
                    self.route_east_west.add(
                        f'{self.leo_con.ground_stations.encode_GS_name(
                            sgid)}_{self.leo_con.ground_stations.encode_GS_name(dgid)}'
                    )

                # Northeast sourth east
                else:
                    self.route_northeast_southwest.add(
                        f'{self.leo_con.ground_stations.encode_GS_name(
                            sgid)}_{self.leo_con.ground_stations.encode_GS_name(dgid)}'
                    )

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
