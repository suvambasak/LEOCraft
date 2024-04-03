import concurrent.futures
import time

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.utilities import k_shortest_paths


class LEOConstellation(Constellation):
    """
    Basic LEO satellite constellation includes number of ground stations

    Computers routes from ground stations to ground stations
    """

    def __init__(self, name: str = 'LEOConstellation', PARALLEL_MODE: bool = True) -> None:
        super().__init__(name, PARALLEL_MODE)

    def generate_routes(self) -> None:
        """Generate K shortest routes from all ground station terminals to all ground station terminals. \n
        - Generate routes in dict with key: `G-X_G-Y`
        - Generate link load dict (number of flow through each link) with key: `tuple(hop, hop)`
        - Records no path found between two GS: set(flow)
        - Records if K path not found between two GS: set(flow, # flow found)

        Parameters
        --------
        k: int
            Number of shortest routes terminal to terminal
        """

        # Stores the routes with a key G-X_G-Y
        self.routes: dict[str, list[list[str]]] = dict()
        # Stores the flow per link with a key (hop, hop)
        self.link_load: dict[tuple[str, str]: set[tuple[str, int]]] = dict()
        self.no_path_found: set[str] = set()
        self.k_path_not_found: set[str] = set()

        start_time = time.perf_counter()

        if self.PARALLEL_MODE:
            self._proutes()
        else:
            self._sroutes()

        self.v.clr()
        end_time = time.perf_counter()
        self.v.log(
            f'''Routes generated in: {
                round((end_time-start_time)/60, 2)}m       '''
        )

    def _proutes(self) -> None:
        "Compute grouts in parallel mode"

        for sgid in range(len(self.ground_stations.terminals)):
            if not self.gsls[sgid]:
                continue

            source = self.ground_stations.encode_name(sgid)
            self.connect_ground_station(source)

            path_compute = set()
            with concurrent.futures.ProcessPoolExecutor() as executor:

                for dgid in range(sgid+1, len(self.ground_stations.terminals)):
                    if not self.gsls[dgid]:
                        continue

                    destination = self.ground_stations.encode_name(dgid)
                    self.connect_ground_station(destination)

                    self.v.rlog(
                        f'''Generating {self.k} routes  ({
                            source} to {destination})  '''
                    )

                    path_compute.add(executor.submit(
                        k_shortest_paths,
                        self.sat_net_graph.copy(),
                        source,
                        destination,
                        self.k
                    ))

                    self.disconnect_ground_station(destination)

                for compute in concurrent.futures.as_completed(path_compute):
                    self.v.rlog(
                        f'''Route processing complete ({round(
                            sgid/len(self.ground_stations.terminals)*100
                        )}%)...       '''
                    )
                    compute_status, flow, k_path = compute.result()
                    self._add_route(compute_status, flow, k_path)

            self.disconnect_ground_station(source)
            self.v.clr()

    def _sroutes(self) -> None:
        "Compute routes in serial mode"

        for sgid in range(len(self.ground_stations.terminals)):
            if not self.gsls[sgid]:
                continue

            source = self.ground_stations.encode_name(sgid)
            self.connect_ground_station(source)

            for dgid in range(sgid+1, len(self.ground_stations.terminals)):
                if not self.gsls[dgid]:
                    continue

                destination = self.ground_stations.encode_name(dgid)
                self.connect_ground_station(destination)

                self.v.rlog(
                    f'''Generating {self.k} routes  ({
                        source} to {destination})  '''
                )

                compute_status, flow, k_path = k_shortest_paths(
                    self.sat_net_graph, source, destination, self.k
                )
                self._add_route(compute_status, flow, k_path)

                self.disconnect_ground_station(destination)
            self.disconnect_ground_station(source)
