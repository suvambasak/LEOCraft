import concurrent.futures
import json
import os
import time
from abc import ABC, abstractmethod

import networkx as nx
from astropy import units as u
from astropy.time import TimeDelta

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.satellite_topology.LEO_sat_topology import (LEOSatelliteTopology,
                                                          SatelliteInfo)
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.user_terminals.terminal import TerminalCoordinates
from LEOCraft.utilities import ProcessingLog


class Constellation(ABC):
    "Abstract class for the LEO constellations"

    ISL_CAPACITY: float = 50.0
    GSL_CAPACITY: float = 20.0
    k: int = 20

    def __init__(self, name: str, PARALLEL_MODE: bool = True) -> None:
        self.PARALLEL_MODE = PARALLEL_MODE

        self.name = name
        self.ground_stations: GroundStation
        self.shells: list[PlusGridShell] = list()

        self.v = ProcessingLog(self.__class__.__name__)

        # Stores the routes with a key G-X_G-Y
        self.routes: dict[str, list[list[str]]]
        # Stores the flow per link with a key (hop, hop)
        self.link_load: dict[tuple[str, str], set[tuple[str, int]]]
        self.no_path_found: set[str]
        self.k_path_not_found: set[str]

    def set_loss_model(self, model: FSPL | None) -> None:
        "Set path-loss model"
        self.loss_model = model

    def set_time(
        self,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        nanosecond: int = 0
    ) -> None:
        """Sets the simulation time, i.e., time passed from the epoch. Default values are zero (0)

        Parameters
        ----------
        day : int, optional
        hour: int, optional
        minute: int, optional
        second: int, optional
        millisecond: int, optional
        nanosecond: int, optional
        """
        self.time_delta = self.calculate_time_delta(
            day, hour, minute, second, millisecond, nanosecond
        )

    @staticmethod
    def calculate_time_delta(
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        nanosecond: int = 0
    ) -> TimeDelta:
        _time_delta = TimeDelta(nanosecond * u.nanosecond)
        _time_delta += TimeDelta(millisecond * u.millisecond)
        _time_delta += TimeDelta(second * u.second)
        _time_delta += TimeDelta(minute * u.minute)
        _time_delta += TimeDelta(hour * u.hour)
        _time_delta += TimeDelta(day * u.day)
        return _time_delta

    def add_ground_stations(self, ground_stations: GroundStation) -> None:
        """Adds ground stations to the constellation

        Parameters
        ------
        ground_stations: GroundStation
            Instance of GroundStation with all the terminals
        """
        self.ground_stations = ground_stations

    def add_shells(self, shell: LEOSatelliteTopology) -> None:
        """Adds LEO satellite shell to the constellation

        Parameters
        ------
        shell: LEOSatelliteTopology
            Instance of LEOSatelliteTopology with LEO satellite topology (satellites and ISLs)
        """
        assert shell.id == len(self.shells), 'Shell ID error'
        self.shells.append(shell)

    def build(self) -> None:
        """Build the constellation
        - Build ground stations
        - Build Shells
        - Generate GSLs
        - Computes satellites coverage
        """

        assert len(self.shells) > 0, 'Atleast one shell required.'

        self.v.log('Building ground stations...')
        self.ground_stations.build()

        self.v.log('Building shells...')
        for shell_id, shell in enumerate(self.shells):
            self.v.rlog(f'Processing...  ({shell_id+1}/{len(self.shells)})')
            shell.build_satellites()
            shell.build_ISLs()
        self.v.clr()

        self.v.log('Building ground to satellite links...')
        # Records of user terminals under satellite coverage
        self.sat_coverage: dict[str, set[str]] = dict()
        # Ground to satellite link records
        # List index is the ground station terminal index
        self.gsls = [None]*len(self.ground_stations.terminals)

        start_time = time.perf_counter()

        if self.PARALLEL_MODE:
            self._pbuild_gsls()
        else:
            self._sbuild_gsls()

        self.v.clr()
        end_time = time.perf_counter()
        self.v.log(
            f'''GSLs generated in: {round((end_time-start_time)/60, 2)}m'''
        )

    def _pbuild_gsls(self) -> None:
        "Compute GSLs in parallel mode"
        with concurrent.futures.ProcessPoolExecutor() as executor:
            gsl_compute = list()
            for gid, gs in enumerate(self.ground_stations.terminals):
                self.gsls[gid] = set()
                self.v.rlog(
                    f'''Processing GSLs...  ({
                        gid+1}/{len(self.ground_stations.terminals)})'''
                )

                # For one terminal computing each shell in parallel
                for shell in self.shells:

                    gsl_compute.append(
                        executor.submit(
                            shell.get_satellites_in_range,
                            gs, gid, self.time_delta
                        )
                    )

            compute_count = 0
            for compute in concurrent.futures.as_completed(gsl_compute):
                compute_count += 1
                self.v.rlog(
                    f'''Processing GSLs completed...   {
                        round(compute_count/len(gsl_compute)*100)}%   '''
                )

                # Collecting results and adding list of GSLs and satellite coverage
                rgid, visible_sats, sats_range_m = compute.result()
                for sat_name, distance_m in zip(visible_sats, sats_range_m):
                    self._add_sat_coverage(
                        sat_name, self.ground_stations.encode_name(rgid)
                    )
                    self.gsls[rgid].add((sat_name, distance_m))

    def _sbuild_gsls(self) -> None:
        "Compute GSLs in serial mode"
        for gid, gs in enumerate(self.ground_stations.terminals):
            self.gsls[gid] = set()
            self.v.rlog(
                f'''Processing GSLs...  ({
                    gid+1}/{len(self.ground_stations.terminals)})'''
            )

            for shell in self.shells:
                _, visible_sats, sats_range_m = shell.get_satellites_in_range(
                    gs, gid, self.time_delta
                )
                for sat_name, distance_m in zip(visible_sats, sats_range_m):
                    self.gsls[gid].add((sat_name, distance_m))
                    self._add_sat_coverage(
                        sat_name, self.ground_stations.encode_name(gid)
                    )

    def _add_sat_coverage(self, sat_name: str, gs_name: str) -> None:
        "Adds ground station name under the coverage of a satellite"
        if sat_name not in self.sat_coverage:
            self.sat_coverage[sat_name] = set()
        self.sat_coverage[sat_name].add(gs_name)

    def _add_satellites_from_shell(self, shell: LEOSatelliteTopology) -> None:
        "Adds encoded satellite name into N/W graph"
        for sid in range(len(shell.satellites)):
            self.sat_net_graph.add_node(shell.encode_sat_name(sid))

    def _add_ISLs_from_shell(self, shell: LEOSatelliteTopology) -> None:
        for sid_a, sid_b in (shell.isls):
            distance_m, in_ISL_range = shell.distance_between_sat_m(
                sid_a, sid_b, self.time_delta
            )

            if not in_ISL_range:
                raise ValueError(
                    "The distance between two satellites (%d and %d) "
                    "with an ISL exceeded the maximum ISL length (%.2fm > %.2fm at time_delta=%d)"
                    % (sid_a, sid_b, distance_m, shell.satellites[sid_a].max_ISL_length_m, self.time_delta)
                )

            self.sat_net_graph.add_edge(
                shell.encode_sat_name(sid_a),
                shell.encode_sat_name(sid_b),
                weight=distance_m,
                capacity=self.ISL_CAPACITY
            )

    def create_network_graph(self) -> None:
        """Create network graph using Networkx
        - Nodes:
            - Ground stations
            - Satellites
        - Edges:
            - GSLs
            - ISLs
        - Edge attributes
            - weight: distance in meters
            - capacity: link_bandwidth in Gbps
        """

        # Satellite network graph
        self.sat_net_graph = nx.Graph()

        # Add satellites from each shell
        self.v.log('Adding satellites into network graph...')
        for shell in self.shells:
            self._add_satellites_from_shell(shell)

        # Add ISLs from each shell
        self.v.log('Adding ISLs into network graph...')
        for shell_id, shell in enumerate(self.shells):
            self.v.rlog(f'Processing... ({shell_id}/{len(self.shells)})')
            self._add_ISLs_from_shell(shell)
        self.v.clr()

    def connect_ground_station(self, *gs_names: tuple[str]) -> None:
        """Adds ground to satellites links to network graph

        Parameters
        -------
        gs_names: tuple[str]
            Tuple of ground station names ('G-X','G-Y')
        """

        for gs_name in gs_names:
            gid = self.ground_stations.decode_name(gs_name)
            for sat_name, distance_m in self.gsls[gid]:
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
                    gs_name, sat_name, weight=distance_m, capacity=link_bandwidth
                )

    def disconnect_ground_station(self, *gs_names: tuple[str]) -> None:
        """Remove ground to satellites links from network graph

        Parameters
        -------
        gs_names: tuple[str]
            Tuple of ground station names ('G-X','G-Y')
        """

        for gs_name in gs_names:
            gid = self.ground_stations.decode_name(gs_name)
            for sat_name, _ in self.gsls[gid]:
                self.sat_net_graph.remove_edge(gs_name, sat_name)

    @abstractmethod
    def generate_routes(self, k: int = 1) -> None:
        """Generate K shortest routes from all terminals to all terminals. \n
        - Generate routes in dict with key: `G-X_G-Y`
        - Generate link load dict (number of flow through each link) with key: `tuple(hop, hop)`
        - Records no path found between two GS: set(flow)
        - Records if K path not found between two GS: set(flow, # flow found)

        Parameters
        --------
        k: int
            Number of shortest routes terminal to terminal
        """
        pass

    def _add_linkload(self, flow_via_route: tuple[str, int], edge: tuple[str, str]) -> None:
        """Add flow details going through a link (edge)

        Parameters
        -------
        flow_via_route: tuple[str, int]
            Flow key (G-X_G-Y) and route index (k) i.e., (G-X_G-Y, k)

        edge: tuple[str, str]
            ISL of GSL link i,e, (G-X, S0-Y)
        """

        # For new edge
        if edge not in self.link_load:
            self.link_load[edge] = set()

        if flow_via_route not in self.link_load[edge]:
            self.link_load[edge].add(flow_via_route)

    def _add_route(self, compute_status: bool, flow: str, k_path: list[list[str]]) -> None:
        '''Post processing of routes routes after  compute

        Parameters
        --------
        compute_status: bool
            Compute status
        flow: str
            Flow name (G-X_G-Y) or (G-X_F-Y)
        k_path: list[list[str]]
            List of K routes
        '''
        # In case no path found
        if False == compute_status:
            self.no_path_found.add(flow)

        # In case K path not found
        # Record the flow and number of path (< k) found
        if compute_status and len(k_path) != self.k:
            self.k_path_not_found.add(f'{flow},{len(k_path)}')
            return

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

    def link_capacity(self, node_a: str, node_b: str) -> float:
        """Get the capacity (Gbps) of a link

        Parameters
        -------
        node_a: str
            Satellite/ground station name  in network graph
        node_b: str
            Satellite/ground station name in network graph

        Returns
        -------
        float
            Data rate in Gbps
        """
        return self.sat_net_graph[node_a][node_b]["capacity"]

    def link_length(self, node_a: str, node_b: str) -> float:
        """Get the length (meters) of a link

        Parameters
        -------
        node_a: str
            Satellite/ground station name  in network graph
        node_b: str
            Satellite/ground station name  in network graph

        Returns
        -------
        float
            Length in meters
        """
        return self.sat_net_graph[node_a][node_b]["weight"]

    def sat_info(self, sat_name: str) -> SatelliteInfo:
        """Get satellite information at current time delta

        Parameters
        ---------
        sat_name: str
            Satellite name

        Returns
        ---------
        tuple[int, int, tuple[float, float]]
            Shell ID, Satellite ID, (lat, long)
        """

        shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)
        return self.shells[shell_id].build_sat_info(sid, self.time_delta)

    def gs_info(self, gs_name: str) -> tuple[int, TerminalCoordinates]:
        """Get ground station information

        Parameters
        ---------
        gs_name: str
            Ground station name

        Returns
        ---------
        tuple[int, TerminalCoordinates]
            Ground station ID, TerminalCoordinates dataclass object
        """

        gid = self.ground_stations.decode_name(gs_name)
        return gid, self.ground_stations.terminals[gid]

    def _create_export_dir(self, prefix_path: str = '.') -> str:
        'Create directory for time delta inside given path (default current directory)'
        dir = f'{prefix_path}/{self.time_delta}'
        if not os.path.isdir(dir):
            os.makedirs(dir, exist_ok=True)
        return dir

    def _write_text_file(self, content: set[str], path_filename: str) -> str:
        'Write a text file separated by new line'
        with open(path_filename, "w") as text_file:
            for line in content:
                text_file.write(f"{line}\n")

        return path_filename

    def _write_json_file(self, content: dict, path_filename: str) -> str:
        'Write dict into a JSON file'
        with open(path_filename, 'w') as json_file:
            json_file.write(json.dumps(content))
        return path_filename

    def export_routes(self, prefix_path: str = '.') -> str:
        """Write routes into a JSON file inside time delta at given path (default current directory)

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
        filename = f'{dir}/{self.name}_routes.json'

        # Write JSON file
        with open(filename, 'w') as json_file:
            json_file.write(json.dumps(self.routes))

        return filename

    def export_no_path_found(self, prefix_path: str = '.') -> str:
        """Write flows with no path into a TXT file inside time delta at given path (default current directory)

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
        filename = f'{dir}/{self.name}_no_path_found.txt'
        return self._write_text_file(self.no_path_found, filename)

    def export_k_path_not_found(self, prefix_path: str = '.') -> str:
        """Write flows with less then k path into a TXT file inside time delta at given path (default current directory)

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
        filename = f'{dir}/{self.name}_k_path_not_found.txt'
        return self._write_text_file(self.k_path_not_found, filename)

    def export_gsls(self, prefix_path: str = '.') -> str:
        """Write GSLs into a JSON file inside time delta at given path (default current directory)

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
        filename = f'{dir}/{self.name}_gsls.json'

        # Convert GSLs in a to dict
        json_data = {}
        for gid, visibility in enumerate(self.gsls):
            json_data[self.ground_stations.encode_name(gid)] = list(visibility)
        return self._write_json_file(json_data, filename)
