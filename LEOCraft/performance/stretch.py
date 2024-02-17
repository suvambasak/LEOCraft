import csv
import statistics
from abc import abstractmethod

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.performance import Performance
from LEOCraft.performance.route_classifier.flow_classifier import \
    FlowClassifier


class Stretch(Performance):
    '''
    Implements Performance for measuring stretch of routes in constellation

    Computes end to end
    - Stretch: Distance over ISLs / Geodesic distance 
    - Hop counts of each routes and median of each route category
    '''

    def __init__(self, leo_con: Constellation) -> None:
        super().__init__(leo_con)

        self._stretch_dataset: list[dict] = list()

        # Stretch results
        self.NS_sth: float
        self.EW_sth: float
        self.HG_sth: float
        self.LG_sth: float
        self.NESW_sth: float

        # Hop counts
        self.NS_cnt: int
        self.EW_cnt: int
        self.HG_cnt: int
        self.LG_cnt: int
        self.NESW_cnt: int

        self._rcategories: FlowClassifier

    def build(self) -> None:
        self.v.nl()
        self.v.log('Building stretch...')
        self._rcategories.classify()

        # Connect all the ground station
        self.v.rlog('Connecting all ground stations...')
        for gid, _ in enumerate(self.leo_con.ground_stations.terminals):
            self.leo_con.connect_ground_station(
                self.leo_con.ground_stations.encode_name(gid)
            )
        self.v.clr()

    def compute(self) -> None:
        self.v.log('Computing stretch...')

        self.NS_sth, self.NS_cnt, _stretch = self._compute_stretch(
            self._rcategories.route_north_south
        )
        self._stretch_dataset.extend(_stretch)
        self.v.log(f'NS stretch:\t{round(self.NS_sth, 3)}')
        self.v.log(f'NS hop count:\t{self.NS_cnt}')

        self.EW_sth, self.EW_cnt, _stretch = self._compute_stretch(
            self._rcategories.route_east_west
        )
        self._stretch_dataset.extend(_stretch)
        self.v.log(f'EW stretch:\t{round(self.EW_sth, 3)}')
        self.v.log(f'EW hop count:\t{self.EW_cnt}')

        self.NESW_sth, self.NESW_cnt, _stretch = self._compute_stretch(
            self._rcategories.route_northeast_southwest
        )
        self._stretch_dataset.extend(_stretch)
        self.v.log(f'NESW stretch:\t{round(self.NESW_sth, 3)}')
        self.v.log(f'NESW hop count:\t{self.NESW_cnt}')

        self.LG_sth, self.LG_cnt, _stretch = self._compute_stretch(
            self._rcategories.route_low_geodesic
        )
        self._stretch_dataset.extend(_stretch)
        self.v.log(f'LG stretch:\t{round(self.LG_sth, 3)}')
        self.v.log(f'LG hop count:\t{self.LG_cnt}')

        self.HG_sth, self.HG_cnt, _stretch = self._compute_stretch(
            self._rcategories.route_high_geodesic
        )
        self._stretch_dataset.extend(_stretch)
        self.v.log(f'HG stretch:\t{round(self.HG_sth, 3)}')
        self.v.log(f'HG hop count:\t{self.HG_cnt}')

    @abstractmethod
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
        pass

    def _end_to_end_distance_over_ISL_m(self, k_routes: list[list[str]]) -> tuple[float, float, float, float]:
        '''Calculates end to end distance over ISLs in meters

        Parameters
        -------
        k_routes: list[list[str]]
            End to end routes in 2D list


        Returns
        --------
        tuple[float, float, float]
            Max distance, Min distance, and Average distance in meters, median hop counts
        '''

        routes_length_m = list()
        routes_hop_count = list()

        # For each route of K routes
        for route in k_routes:
            route_length_m = 0

            # Each edge in that route
            for hop in range(len(route)-1):
                route_length_m += self.leo_con.link_length(
                    route[hop], route[hop+1]
                )
            routes_length_m.append(route_length_m)
            routes_hop_count.append(len(route))

        return (
            max(routes_length_m),
            min(routes_length_m),
            statistics.mean(routes_length_m),
            statistics.median(routes_hop_count)
        )

    def export_stretch_dataset(self, prefix_path: str = '.') -> str:
        '''Writes stretch dataset into a CSV file

        Returns
        --------
        str
            Path of the written file
        '''

        # Get the directory of time delta
        dir = self._create_export_dir(prefix_path)

        # Write inside time delta
        filename = f'{dir}/stretch.csv'

        # Write CSV file
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._stretch_dataset[0].keys()
            )
            writer.writeheader()
            writer.writerows(self._stretch_dataset)

        return filename
