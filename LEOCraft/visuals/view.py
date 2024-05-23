from abc import ABC, abstractmethod

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.utilities import ProcessingLog


class Render(ABC):
    '''
    Abstarct class manages the unique components in view dataclass. 
    All the image and plot generators should extent the class and 
    implement the build method to add all the components from the instance of view dataclass
    '''

    # _COVERAGE_COLOR = "#FF6666"
    _COVERAGE_COLOR = "rgb(255,102,102)"
    _GROUND_STATION_COLOR = "rgb(15,157,88)"
    _GSL_COLOR = "rgb(219,68,55)"
    _ISL_COLOR = "rgb(244,160,0)"
    _R_ISL_COLOR = "rgb(153, 51, 255)"
    _SHELL_COLORS = [
        'rgb(226, 133, 244)',
        'rgb(142, 133, 244)',
        'rgb(96, 52, 33)',
        'rgb(30, 41, 33)',
        'rgb(102, 63, 89)',
        'rgb(46, 182, 191)',
        'rgb(205, 79, 81)',
        'rgb(246, 0, 244)',
        'rgb(94, 41, 191)',
        'rgb(66,133,244)'
    ]

    _DEFAULT_WIDTH = 3
    _THICK_WIDTH = 5

    _sat: set[str]
    _gs: set[str]

    _gsl: set[str]
    _isl: set[tuple[str, str]]

    _cov: set[str]

    _rlink: set[tuple[str, str]]

    # Satellite to be tracked or need attention
    _special_sats: set[str]

    def __init__(self, leo_con: Constellation) -> None:
        self.v = ProcessingLog(self.__class__.__name__)
        self.leo_con = leo_con

        # Keep track of unique objects in view
        self._sat = set()
        self._gs = set()
        self._isl = set()
        self._gsl = set()
        self._cov = set()

        # Links belong to routes view
        self._rlink = set()

        # Satellite to be tracked or need attention
        self._special_sats: set[str] = set()

        for gid in range(len(self.leo_con.gsls)):
            self.leo_con.connect_ground_station(
                self.leo_con.ground_stations.encode_name(gid)
            )

    def highlight_satellites(self, sat_names: list[str]) -> None:
        '''Marks satellites with large markers

        Paramters
        --------
        sat_names: list[str]
            List of sat names
        '''
        self._special_sats.update(sat_names)

    def _valid_sat_name(self, sat_name: str) -> None:
        shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)

        assert len(self.leo_con.shells) >= shell_id, "Incorrect Shell ID"
        assert len(
            self.leo_con.shells[shell_id].satellites
        ) >= sid, "Incorrect satellite"

    def _valid_gs_name(self, gs_name: str) -> None:
        assert self.leo_con.ground_stations.decode_name(gs_name) <= len(
            self.leo_con.ground_stations.terminals
        ), "Incorrent GS"

    def add_ground_stations(self, *gs_names: tuple[str]) -> None:
        '''Add ground stations for rendering

        Parameters
        --------
        gs_names: tuple[str]
            Ground station names
        '''

        for gs_name in gs_names:
            if gs_name in self._gs:
                continue
            self._valid_gs_name(gs_name)
            self._gs.add(gs_name)

    def add_all_ground_stations(self) -> None:
        'Add all the ground stations for rendering'

        for gid in range(len(self.leo_con.ground_stations.terminals)):
            self._gs.add(self.leo_con.ground_stations.encode_name(gid))

    def add_GSLs(self, *gs_names: tuple[str]) -> None:
        '''Add ground to satellite link for rendering

        Parameters
        --------
        gs_names: tuple[str]
            Ground station names
        '''

        for gs_name in gs_names:
            if gs_name in self._gsl:
                continue
            self._valid_gs_name(gs_name)
            self._gsl.add(gs_name)

    def add_all_GSLs(self) -> None:
        'Add all ground to satellite link for rendering'

        for gid in range(len(self.leo_con.ground_stations.terminals)):
            self._gsl.add(self.leo_con.ground_stations.encode_name(gid))

    def add_satellites(self, *sat_names: tuple[str]) -> None:
        '''Add satellites for rendering

        Parameters
        --------
        sat_names: tuple[str]
            Satellite names
        '''

        for sat_name in sat_names:
            if sat_name in self._sat:
                continue
            self._valid_sat_name(sat_name)
            self._sat.add(sat_name)

    def add_all_satellites(self, shell_ids: tuple[int] = None) -> None:
        '''Add all satellites for rendering 
        if the shell id is given then all the satellites from these shell are added for rendering

        Parameters
        --------
         shell_ids: tuple[int], optional
            Shell ids, Default None
        '''

        for shell_id, shell in enumerate(self.leo_con.shells):
            if (None == shell_ids) or (shell_id in shell_ids):
                for sid in range(len(shell.satellites)):
                    self._sat.add(shell.encode_sat_name(sid))

    def add_coverages(self, *sat_names: tuple[str]) -> None:
        '''Add satellites for coverage rendering

        Parameters
        --------
        sat_names: tuple[str]
            Satellite names
        '''

        for sat_name in sat_names:
            if sat_name in self._cov:
                continue
            self._valid_sat_name(sat_name)
            self._cov.add(sat_name)

    def add_all_coverages(self, shell_ids: tuple[int] = None) -> None:
        '''Add all satellites for coverage rendering 
        if the shell id is given then all the satellites from these shell are added for coverage  rendering

        Parameters
        --------
         shell_ids: tuple[int], optional
            Shell ids, Default None
        '''

        for shell_id, shell in enumerate(self.leo_con.shells):
            if (None == shell_ids) or (shell_id in shell_ids):
                for sid in range(len(shell.satellites)):
                    self._cov.add(shell.encode_sat_name(sid))

    def add_ISLs(self, isls: tuple[tuple[str, str]]) -> None:
        '''Add inter satellite links for rendering

        Parameters
        --------
        isls: tuple[tuple[str, str]]
            (Satellite name 1, Satellite name 2)
        '''
        for sat_name_a, sat_name_b in isls:
            if (sat_name_a, sat_name_b) in self._isl:
                continue
            self._valid_sat_name(sat_name_a)
            self._valid_sat_name(sat_name_b)
            self._isl.add((sat_name_a, sat_name_b))

    def add_all_ISLs(self, shell_ids: tuple[int] = None) -> None:
        '''Add all  inter satellite links for  rendering 
        if the shell id is given then all the  inter satellite links from these shell are added for rendering

        Parameters
        --------
         shell_ids: tuple[int], optional
            Shell ids, Default None
        '''

        for shell_id, shell in enumerate(self.leo_con.shells):
            if (None == shell_ids) or (shell_id in shell_ids):
                for sat_a, sat_b in shell.isls:
                    self._isl.add((
                        shell.encode_sat_name(sat_a),
                        shell.encode_sat_name(sat_b)
                    ))

    def _add_route_link(self, hop_a: str, hop_b: str) -> None:
        if hop_a < hop_b:
            self._rlink.add(f'{hop_a}{hop_b}')
        else:
            self._rlink.add(f'{hop_b}{hop_a}')

    def _is_route_link(self, hop_a: str, hop_b: str) -> bool:
        if hop_a < hop_b:
            return f'{hop_a}{hop_b}' in self._rlink
        return f'{hop_b}{hop_a}' in self._rlink

    def add_routes(self, *flows: tuple[str], k: int = 0) -> None:
        '''Add end to end route for rendering (from GS to GSL to ISL to GSl to GS)
        If K is given then only k-1 th routes will be added into the view 

        Parameters
        --------
        flows: tuple[str]
            Flow name i.e. (G-X_G-Y)
        k: int, optional
            k-th shortest path
        '''

        def _process_routes_links(path: list[str]) -> None:
            # First and Last GSL
            self._add_route_link(path[0], path[1])
            self._add_route_link(path[-1], path[-2])

            for hop in range(1, len(path)-2):
                self._add_route_link(path[hop], path[hop+1])
                self.add_ISLs(((path[hop], path[hop+1]),))
                self.add_satellites(path[hop], path[hop+1])

        for flow in flows:
            assert flow in self.leo_con.routes.keys(), "Flow not found in routes"
            sgs, dgs = flow.split('_')

            self.add_ground_stations(sgs, dgs)
            self.add_GSLs(sgs, dgs)

            # If K is given
            if k:
                assert k-1 <= self.leo_con.k
                path = self.leo_con.routes[flow][k-1]
                _process_routes_links(path)

            # If K not not given (k=0), adding all the k routes in view
            else:
                for path in self.leo_con.routes[flow]:
                    _process_routes_links(path)

    def add_all_routes(self) -> None:
        'Add all end to end route for rendering'

        assert len(self.leo_con.routes.keys()) > 0, "No routes"
        for flow in self.leo_con.routes.keys():
            self.add_routes(flow)

    def get_thickness(self, hop_a: str, hop_b: str) -> int:
        '''GSL and ISL link line thickness

        Parameters
        --------
        hop_a: str
            First hop name
        hop_b: str
            Second hop name

        Returns
        -------
        int
            Thickness
        '''

        return self._THICK_WIDTH if self._is_route_link(
            hop_a, hop_b
        ) else self._DEFAULT_WIDTH

    def get_color(self, hop_a: str, hop_b: str) -> int:
        '''GSL and ISL link line thickness

        Parameters
        --------
        hop_a: str
            First hop name
        hop_b: str
            Second hop name

        Returns
        -------
        int
            Thickness
        '''

        return self._R_ISL_COLOR if self._is_route_link(
            hop_a, hop_b
        ) else self._ISL_COLOR

    @abstractmethod
    def build(self) -> None:
        'Render all the element from the view set'
        pass

    @abstractmethod
    def show(sef) -> None:
        'Show plots'
