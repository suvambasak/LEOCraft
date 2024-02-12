import concurrent.futures
import statistics
import time

import psutil

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.user_terminals.aircraft import Aircraft
from LEOCraft.user_terminals.terminal import TerminalCoordinates
from LEOCraft.utilities import k_shortest_paths


class LEOAviationConstellation(Constellation):

    def __init__(self, name: str = 'LEOAviationConstellation') -> None:
        super().__init__(name)

        self.aircrafts: Aircraft

    def add_aircrafts(self, aircrafts: Aircraft) -> None:
        """Adds Aircraft to the constellation

        Parameters
        ------
        aircrafts: Aircraft
            Instance of aircrafts: Aircraft with all the flight terminals
        """
        self.aircrafts = aircrafts

    def build(self) -> None:
        super().build()

        self.v.log('Building flights...')
        self.aircrafts.build()

        self.v.log('Building flight to satellite links...')
        # Flight to satellite link records
        # List index is the flight terminal index
        self.fsls = [None]*len(self.aircrafts.terminals)

        start_time = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            fsl_compute = list()
            for fid, fterminal in enumerate(self.aircrafts.terminals):
                self.fsls[fid] = set()
                self.v.rlog(f'''Processing FSLs...  ({
                            fid+1}/{len(self.aircrafts.terminals)})''')

                for shell in self.shells:

                    fsl_compute.append(
                        executor.submit(
                            self._build_fsl_cluster,
                            fid, fterminal, shell
                        )
                    )

            compute_count = 0
            for compute in concurrent.futures.as_completed(fsl_compute):
                compute_count += 1
                self.v.rlog(f'''Processing FSLs completed...   {
                            round(compute_count/len(fsl_compute)*100)}%''')

                rfid, rfsl_cluster = compute.result()
                for sat_name, distance_m in rfsl_cluster.items():
                    self.fsls[rfid].add((sat_name, distance_m))
                    self._add_sat_coverage(
                        sat_name, self.aircrafts.encode_name(rfid)
                    )

            self.v.clr()
            end_time = time.perf_counter()
            self.v.log(
                f'FSLs generated in: {round((end_time-start_time)/60, 2)}m'
            )

    def _build_fsl_cluster(self, fid: int, fterminal: TerminalCoordinates, shell: LEOSatelliteTopology) -> tuple[int, dict[str, float]]:
        fsl_cluster = dict()

        for flight in self.aircrafts.flights[fterminal.name]:
            _, visible_sats, sats_range_m = shell.get_satellites_in_range(
                flight, fid, self.time_delta
            )

            for sat_name, dist_m in zip(visible_sats, sats_range_m):
                if sat_name not in fsl_cluster.keys():
                    fsl_cluster[sat_name] = list()

                fsl_cluster[sat_name].append(dist_m)

        for sat_name in fsl_cluster.keys():
            fsl_cluster[sat_name] = statistics.mean(fsl_cluster[sat_name])

        return fid, fsl_cluster

    def export_fsls(self, prefix_path: str = '.') -> str:
        """Write FSLs into a JSON file inside time delta at given path (default current directory)

        Parameters
        ----------
        prefix_path: str, optional
            File directory

        Returns
        -------
        str
            File name 
        """
        # Create directory with time delta
        dir = self._create_export_dir(prefix_path)
        filename = f'{dir}/{self.name}_fsls.json'

        # Convert GSLs in a to dict
        json_data = {}
        for fid, visibility in enumerate(self.fsls):
            json_data[self.aircrafts.encode_name(fid)] = list(visibility)
        return self._write_json_file(json_data, filename)

    def connect_flight_cluster_terminals(self, *f_names: tuple[str]) -> None:
        """Adds flight cluster to satellites links to network graph

        Parameters
        -------
        f_names: tuple[str]
            Tuple of flight_cluster_terminal names ('F-X','F-Y')
        """

        for f_name in f_names:
            fid = self.aircrafts.decode_name(f_name)
            for sat_name, distance_m in self.fsls[fid]:
                # When pathloss model is available
                if self.loss_model:
                    link_bandwidth = self.loss_model.data_rate_bps(
                        distance_m, len(self.sat_coverage[sat_name])
                    )/1000000000

                # When pathloss model is not available
                else:
                    link_bandwidth = round(
                        self.GSL_CAPACITY/len(self.sat_coverage[sat_name])
                    )

                self.sat_net_graph.add_edge(
                    f_name, sat_name, weight=distance_m, capacity=link_bandwidth
                )

    def disconnect_flight_cluster_terminals(self, *f_names: tuple[str]) -> None:
        """Removes flight cluster to satellites links to network graph

        Parameters
        -------
        f_names: tuple[str]
            Tuple of flight_cluster_terminal names ('F-X','F-Y')
        """

        for f_name in f_names:
            fid = self.aircrafts.decode_name(f_name)
            for sat_name, _ in self.fsls[fid]:
                self.sat_net_graph.remove_edge(f_name, sat_name)

    def generate_routes(self) -> None:
        """Generate K shortest routes from all ground station terminals to all flight terminals. \n
        - Generate routes in dict with key: `G-X_F-Y`
        - Generate link load dict (number of flow through each link) with key: `tuple(hop, hop)`
        - Records no path found between two GS: set(flow)
        - Records if K path not found between two GS: set(flow, # flow found)

        Parameters
        --------
        k: int
            Number of shortest routes terminal to terminal
        """

        # Stores the routes with a key G-X_F-Y
        self.routes: dict[str, list[list[str]]] = dict()
        # Stores the flow per link with a key (hop, hop)
        self.link_load: dict[tuple[str, str]: set[tuple[str, int]]] = dict()
        self.no_path_found: set[str] = set()
        self.k_path_not_found: set[str] = set()

        start_time = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            path_compute = set()

            _no_route_log = ''
            for gid in range(len(self.ground_stations.terminals)):
                for fid in range(len(self.aircrafts.terminals)):

                    source = self.ground_stations.encode_name(gid)
                    destination = self.aircrafts.encode_name(fid)

                    # In case of no GSL/FSL from source GS or destination Flight cluster
                    if not (self.gsls[gid] and self.fsls[fid]):
                        _no_route_log = f'''| No route from ({source} to {
                            destination})'''
                        continue

                    self.v.rlog(f'''Generating {self.k} routes  ({
                                source} to {destination})  {_no_route_log}  ''')

                    self.connect_ground_station(source)
                    self.connect_flight_cluster_terminals(destination)

                    # Compute K shortest path in parallel
                    path_compute.add(executor.submit(
                        k_shortest_paths,
                        self.sat_net_graph.copy(),
                        source,
                        destination,
                        self.k
                    ))

                    self.disconnect_ground_station(source)
                    self.disconnect_flight_cluster_terminals(destination)

                if 80 < psutil.virtual_memory().percent:
                    self.v.rlog('Waiting for queuing...        ')
                    time.sleep(1)

            compute_count = 0
            for compute in concurrent.futures.as_completed(path_compute):
                compute_status, flow, k_path = compute.result()

                compute_count += 1
                self.v.rlog(
                    f'''Generating {self.k} routes completed... {
                        round(compute_count/len(path_compute)*100)}%  '''
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
                    self._add_linkload(
                        flow_via_route, (path[-1], path[-2]))

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
            f'Routes generated in: {
                round((end_time-start_time)/60, 2)}m       '
        )
