import statistics

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.stretch import Stretch
from LEOCraft.performance.route_classifier.aviation_classifier import \
    AviationClassifier


class Stretch(Stretch):
    '''
    Implements Performance for measuring stretch of routes in constellation

    Computes end to end
    - Stretch: Distance over ISLs / Geodesic distance 
    - Hop counts of each routes and median of each route category
    '''

    def __init__(self, leo_con: Constellation) -> None:
        super().__init__(leo_con)

        self._rcategories = AviationClassifier(self.leo_con)

    def build(self) -> None:
        super().build()

        # Adding FSLs
        self.v.rlog('Connecting all flight terminals...')
        for tid, _ in enumerate(self.leo_con.aircrafts.terminals):
            self.leo_con.connect_flight_cluster_terminals(
                self.leo_con.aircrafts.encode_name(tid)
            )
        self.v.clr()

    def _compute_stretch(self, flows: set[str]) -> tuple[float, float, list[dict]]:
        '''Computes the stretch dataset of a flow category

        Parameters
        -------
        flows: set[str]
            Set of flows

        Returns
        ------
        tuple[float, list[dict]]
            Median stretch of the category, median hop count of the category, list of dict info about all the flows of the category
        '''

        _stretch: list[dict] = list()

        for flow in flows:
            # When flow not exist in routes of constellation
            if flow not in self.leo_con.routes.keys():
                continue

            # Extract GS id
            source_GS, destination_flight = flow.split('_')
            gid = self.leo_con.ground_stations.decode_name(source_GS)
            fid = self.leo_con.aircrafts.decode_name(destination_flight)

            # Geodesic distance B/W endpoint (GS to GS)
            geodesic_dist_m = self.leo_con.ground_stations.geodesic_distance_between_terminals_m(
                self.leo_con.ground_stations.terminals[gid],
                self.leo_con.aircrafts.terminals[fid]
            )

            # Distance and median hop count over ISLs
            max_ISL_dist_m, min_ISL_dist_m, avg_ISL_dist_m, mhop_count = self._end_to_end_distance_over_ISL_m(
                self.leo_con.routes[flow]
            )

            _stretch.append({
                'source': source_GS,
                'destination': destination_flight,

                'max_stretch': max_ISL_dist_m/geodesic_dist_m,
                'min_stretch': min_ISL_dist_m/geodesic_dist_m,
                'avg_stretch': avg_ISL_dist_m/geodesic_dist_m,

                'geodesic_dist_km': geodesic_dist_m/1000,

                'max_ISL_dist_km': max_ISL_dist_m/1000,
                'min_ISL_dist_km': min_ISL_dist_m/1000,
                'avg_ISL_dist_km': avg_ISL_dist_m/1000,

                'mid_hop_cnt': mhop_count

            })

        # List of min stretch extracted
        min_stretch_list = [sth['min_stretch'] for sth in _stretch]
        # List of median hop count
        median_hop_count_list = [sth['mid_hop_cnt'] for sth in _stretch]

        return (
            statistics.median(min_stretch_list) if min_stretch_list else 0,
            statistics.median(
                median_hop_count_list
            ) if median_hop_count_list else 0,
            _stretch
        )
