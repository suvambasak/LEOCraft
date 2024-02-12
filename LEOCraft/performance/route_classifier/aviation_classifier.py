from LEOCraft.performance.route_classifier.flow_classifier import \
    FlowClassifier
from LEOCraft.user_terminals.ground_station import GroundStation


class AviationClassifier(FlowClassifier):
    'Create categories based on the based on the relative position of the source ground station and destination flight terminal'

    def classify(self) -> None:
        'Classify the routes based on position of ground stations and flight terminal'

        for gid in range(len(self.leo_con.ground_stations.terminals)):
            for fid in range(len(self.leo_con.aircrafts.terminals)):

                geodesic_m = GroundStation.geodesic_distance_between_terminals_m(
                    self.leo_con.ground_stations.terminals[gid],
                    self.leo_con.aircrafts.terminals[fid]
                )

                # High geodesic
                if geodesic_m > self._HIGH_GEODESIC_BOUND_M:
                    self.route_high_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            gid)}_{self.leo_con.aircrafts.encode_name(fid)}'
                    )
                    continue

                # Low geodesic
                if geodesic_m < self._LOW_GEODESIC_BOUND_M:
                    self.route_low_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            gid)}_{self.leo_con.aircrafts.encode_name(fid)}'
                    )
                    continue

                slope, slope_in_degrees = self.calculate_slope(
                    self.leo_con.ground_stations.terminals[gid],
                    self.leo_con.aircrafts.terminals[fid]
                )

                # Invalid slope
                if 90 < abs(slope_in_degrees):
                    raise ValueError(
                        self.leo_con.ground_stations.terminals[gid],
                        self.leo_con.aircrafts.terminals[fid],
                        slope, slope_in_degrees
                    )
                if 0 > abs(slope_in_degrees):
                    raise ValueError(
                        self.leo_con.ground_stations.terminals[gid],
                        self.leo_con.aircrafts.terminals[fid],
                        slope, slope_in_degrees
                    )

                # North south routes
                if self._NORTH_SOUTH_BOUND_DEGREE < abs(slope_in_degrees):
                    self.route_north_south.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            gid)}_{self.leo_con.aircrafts.encode_name(fid)}'
                    )

                # East west routes
                elif self._EAST_WEST_BOUND_DEGREE > abs(slope_in_degrees):
                    self.route_east_west.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            gid)}_{self.leo_con.aircrafts.encode_name(fid)}'
                    )

                # Northeast sourth east
                else:
                    self.route_northeast_southwest.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            gid)}_{self.leo_con.aircrafts.encode_name(fid)}'
                    )
