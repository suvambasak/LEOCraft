import concurrent.futures
import time

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.utilities import k_shortest_paths


class LEOConstellation(Constellation):
    """
    Basic LEO satellite constellation includes number of ground stations

    Computers routes from ground stations to ground stations
    """

    def __init__(self, name: str = 'LEOConstellation') -> None:
        super().__init__(name)

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
        with concurrent.futures.ProcessPoolExecutor() as executor:
            path_compute = list()

            for sgid in range(len(self.ground_stations.terminals)):
                for dgid in range(sgid+1, len(self.ground_stations.terminals)):
                    source = self.ground_stations.encode_name(sgid)
                    destination = self.ground_stations.encode_name(dgid)

                    # In case of no GSL from source GS or destination GS
                    if not (self.gsls[sgid] and self.gsls[dgid]):
                        self.v.rlog(
                            f'No route from ({source} to {destination})       '
                        )
                        continue

                    self.v.rlog(
                        f'Generating {self.k} routes  ({source} to {
                            destination})'
                    )

                    self.connect_ground_station(source, destination)

                    # Compute K shortest path in parallel
                    path_compute.append(executor.submit(
                        k_shortest_paths,
                        self.sat_net_graph.copy(),
                        source,
                        destination,
                        self.k
                    ))

                    self.disconnect_ground_station(source, destination)

            compute_count = 0
            for compute in concurrent.futures.as_completed(path_compute):
                compute_status, flow, k_path = compute.result()

                compute_count += 1
                self.v.rlog(
                    f'Generating {self.k} routes completed... {
                        round(compute_count/len(path_compute)*100)} % '
                )

                # In case no path found
                if False == compute_status:
                    self.no_path_found.add(flow)

                # In case K path not found
                # Record the flow and number of path (< k) found
                if compute_status and len(k_path) != self.k:
                    self.k_path_not_found.add(f'{flow},{len(k_path)}')
                    continue

                # Storing the routes
                self.routes[flow] = k_path

                # Recording total flows passing through each link
                for k_index, path in enumerate(k_path):
                    flow_via_route = (flow, k_index)

                    # Two end links (ground station to satellite)
                    self._add_linkload(flow_via_route, (path[0], path[1]))
                    self._add_linkload(flow_via_route, (path[-1], path[-2]))

                    # All intermmidiate links
                    for hop in range(1, len(path)-2):
                        # Adding load in order
                        if path[hop] < path[hop+1]:
                            self._add_linkload(
                                flow_via_route, (path[hop], path[hop+1])
                            )
                        else:
                            self._add_linkload(
                                flow_via_route, (path[hop+1], path[hop])
                            )

            self.v.clr()
            end_time = time.perf_counter()
            self.v.log(
                f'Routes generated in: {round((end_time-start_time)/60, 2)}m'
            )
