from LEOCraft.performance.route_classifier.flow_classifier import \
    FlowClassifier
from LEOCraft.user_terminals.ground_station import GroundStation


class BasicClassifier(FlowClassifier):
    'Create categories based on the based on the relative position of the source/destination ground stations'

    def classify(self) -> None:
        'Classify the routes based on position of source/destination ground stations'

        for sgid in range(len(self.leo_con.ground_stations.terminals)):
            for dgid in range(sgid+1, len(self.leo_con.ground_stations.terminals)):

                geodesic_m = GroundStation.geodesic_distance_between_terminals_m(
                    self.leo_con.ground_stations.terminals[sgid],
                    self.leo_con.ground_stations.terminals[dgid]
                )

                # High geodesic
                if geodesic_m > self._HIGH_GEODESIC_BOUND_M:
                    self.route_high_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            sgid)}_{self.leo_con.ground_stations.encode_name(dgid)}'
                    )
                    continue

                # Low geodesic
                if geodesic_m < self._LOW_GEODESIC_BOUND_M:
                    self.route_low_geodesic.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            sgid)}_{self.leo_con.ground_stations.encode_name(dgid)}'
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
                if self._NORTH_SOUTH_BOUND_DEGREE < abs(slope_in_degrees):
                    self.route_north_south.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            sgid)}_{self.leo_con.ground_stations.encode_name(dgid)}'
                    )

                # East west routes
                elif self._EAST_WEST_BOUND_DEGREE > abs(slope_in_degrees):
                    self.route_east_west.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            sgid)}_{self.leo_con.ground_stations.encode_name(dgid)}'
                    )

                # Northeast sourth east
                else:
                    self.route_northeast_southwest.add(
                        f'{self.leo_con.ground_stations.encode_name(
                            sgid)}_{self.leo_con.ground_stations.encode_name(dgid)}'
                    )
