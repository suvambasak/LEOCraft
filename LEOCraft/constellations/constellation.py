import json
import os
from abc import ABC, abstractmethod

import ephem
import networkx as nx
from astropy import units as u
from astropy.time import TimeDelta

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.satellite import LEOSatellite
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.user_terminals.terminal_coordinates import TerminalCoordinates
from LEOCraft.utilities import ProcessingLog


class Constellation(ABC):
    "Abstract class for the LEO constellations"

    ISL_CAPACITY: float = 50.0
    GSL_CAPACITY: float = 20.0
    k: int

    def __init__(self, name: str) -> None:
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
        self.v.log('Building ground stations...')
        self.ground_stations.build()

        self.v.log('Building shells...')
        for shell_id, shell in enumerate(self.shells):
            self.v.rlog(f'Processing... ({shell_id+1}/{len(self.shells)})')
            shell.build_satellites()
            shell.build_ISLs()
        self.v.clr()

        self.v.log('Building ground to satellite links...')
        # Ground to satellite link records
        # List index is the ground station index
        self.gsls: list[list[tuple[str, float]]] = list()

        # Records of user terminals under satellite coverage
        self.sat_coverage: dict[str, set[str]] = dict()

        for gid, gs in enumerate(self.ground_stations.terminals):
            _gsls: list[tuple[str, float]] = []  # List of GSLs of current gs

            for shell_id, shell in enumerate(self.shells):
                for sid, sat in enumerate(shell.satellites):
                    self.v.rlog(
                        f'Processing GSLs... {
                            gid+1}/{len(self.ground_stations.terminals)}'
                    )

                    distance_m = self.distance_between_terminal_sat_m(gs, sat)
                    # Out of range so GSL not possible
                    if distance_m > sat.max_GSL_length_m():
                        continue
                    _gsls.append((shell.encode_sat_name(sid), distance_m))
                    self._add_sat_coverage(
                        shell.encode_sat_name(sid),
                        self.ground_stations.encode_GS_name(gid)
                    )

            # Adding list of GSL of current gs
            self.gsls.append(_gsls)
        self.v.clr()

    def distance_between_terminal_sat_m(self, terminal: TerminalCoordinates, sat: LEOSatellite) -> float:
        """Computes the straight distance between a ground station and a satellite in meters

        Parameters
        -------------
        terminal: TerminalCoordinates
            Location coordinates of a user terminal
        sat: LEOSatellite
            LEO satellite

        Returns
        ------------
        float
            The distance between the ground station and the satellite in meters
        """

        # Create an observer on the planet where the ground station is
        observer = ephem.Observer()
        observer.epoch = str(sat.epoch)
        observer.date = str(sat.epoch+self.time_delta)

        # Very important: string argument is in degrees.
        # DO NOT pass a float as it is interpreted as radians
        observer.lat = str(terminal.latitude_degree)
        observer.lon = str(terminal.longitude_degree)
        observer.elevation = terminal.elevation_m

        # Compute distance from satellite to observer
        sat.satellite.compute(observer)

        # Return distance
        return sat.satellite.range

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
            gid = self.ground_stations.decode_GS_name(gs_name)
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
            gid = self.ground_stations.decode_GS_name(gs_name)
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

    def _create_export_dir(self, prefix_path: str = '.') -> str:
        'Create directory for time delta inside given path (default current directory)'
        dir = f'{prefix_path}/{self.time_delta}'
        if not os.path.isdir(dir):
            os.makedirs(dir, exist_ok=True)
        return dir

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

    def _write_text_file(self, path_filename: str) -> str:
        'Write a text file separated by new line'
        with open(path_filename, "w") as text_file:
            for line in self.no_path_found:
                text_file.write(f"{line}\n")

        return path_filename

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
        return self._write_text_file(filename)

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
        return self._write_text_file(filename)
