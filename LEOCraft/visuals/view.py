from abc import ABC, abstractmethod
from dataclasses import dataclass

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.utilities import ProcessingLog


@dataclass
class View:
    "Keep track of components in view to be rendered at the time of build"

    sat: set[str]
    gs: set[str]

    gsl: set[str]
    isl: set[tuple[str, str]]

    cov: set[str]


class Render(ABC):
    '''
    Abstarct class manages the unique components in view dataclass. 
    All the image and plot generators should extent the class and 
    implement the build method to add all the components from the instance of view dataclass
    '''

    def __init__(self, leo_con: Constellation) -> None:
        self.v = ProcessingLog(self.__class__.__name__)
        self.leo_con = leo_con

        self.view = View(sat=set(), gs=set(), isl=set(), gsl=set(), cov=set())

    def _valid_sat_name(self, sat_name: str):
        shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)

        assert len(self.leo_con.shells) >= shell_id, "Incorrect Shell ID"
        assert len(
            self.leo_con.shells[shell_id].satellites
        ) >= sid, "Incorrect satellite"

    def _valid_gs_name(self, gs_name: str):
        assert self.leo_con.ground_stations.decode_name(gs_name) <= len(
            self.leo_con.ground_stations.terminals), "Incorrent GS"

    def add_ground_stations(self, *gs_names: tuple[str]) -> None:
        '''Add ground stations for rendering

        Parameters
        --------
        gs_names: tuple[str]
            Ground station names

        '''

        for gs_name in gs_names:
            if gs_name in self.view.gs:
                continue
            self._valid_gs_name(gs_name)
            self.view.gs.add(gs_name)

    def add_all_ground_stations(self) -> None:
        'Add all the ground stations for rendering'

        for gid in range(len(self.leo_con.ground_stations.terminals)):
            self.view.gs.add(self.leo_con.ground_stations.encode_name(gid))

    def add_GSLs(self, *gs_names: tuple[str]) -> None:
        '''Add ground to satellite link for rendering

        Parameters
        --------
        gs_names: tuple[str]
            Ground station names

        '''

        for gs_name in gs_names:
            if gs_name in self.view.gsl:
                continue
            self._valid_gs_name(gs_name)
            self.view.gsl.add(gs_name)

    def add_all_GSLs(self) -> None:
        'Add all ground to satellite link for rendering'

        for gid in range(len(self.leo_con.ground_stations.terminals)):
            self.view.gsl.add(self.leo_con.ground_stations.encode_name(gid))

    def add_satellites(self, *sat_names: tuple[str]) -> None:
        '''Add satellites for rendering

        Parameters
        --------
        sat_names: tuple[str]
            Satellite names
        '''

        for sat_name in sat_names:
            if sat_name in self.view.sat:
                continue
            self._valid_sat_name(sat_name)
            self.view.sat.add(sat_name)

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
                    self.view.sat.add(shell.encode_sat_name(sid))

    def add_coverages(self, *sat_names: tuple[str]) -> None:
        '''Add satellites for coverage rendering

        Parameters
        --------
        sat_names: tuple[str]
            Satellite names
        '''

        for sat_name in sat_names:
            if sat_name in self.view.cov:
                continue
            self._valid_sat_name(sat_name)
            self.view.cov.add(sat_name)

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
                    self.view.cov.add(shell.encode_sat_name(sid))

    def add_ISLs(self, isls: tuple[tuple[str, str]]) -> None:
        '''Add inter satellite links for rendering

        Parameters
        --------
        isls: tuple[tuple[str, str]]
            (Satellite name 1, Satellite name 2)
        '''
        for sat_name_a, sat_name_b in isls:
            if (sat_name_a, sat_name_b) in self.view.isl:
                continue
            self._valid_sat_name(sat_name_a)
            self._valid_sat_name(sat_name_b)
            self.view.isl.add((sat_name_a, sat_name_b))

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
                    self.view.isl.add((
                        shell.encode_sat_name(sat_a),
                        shell.encode_sat_name(sat_b)
                    ))

    def add_routes(self, *flows: tuple[str]) -> None:
        '''Add end to end route for rendering
        From GS to GSL to ISL to GSl to GS

        Parameters
        --------
        flows: tuple[str]
            Flow name i.e. (G-X_G-Y)
        '''

        for flow in flows:
            assert flow in self.leo_con.routes.keys(), "Flow not found in routes"
            sgs, dgs = flow.split('_')
            self.add_ground_stations(sgs, dgs)
            self.add_GSLs(sgs, dgs)
            for path in self.leo_con.routes[flow]:
                for hop in range(1, len(path)-2):
                    self.add_ISLs(((path[hop], path[hop+1]),))
                    self.add_satellites(path[hop], path[hop+1])

    def add_all_routes(self) -> None:
        'Add all end to end route for rendering'

        assert len(self.leo_con.routes.keys()) > 0, "No routes"
        for flow in self.leo_con.routes.keys():
            self.add_routes(flow)

    @abstractmethod
    def build(self) -> None:
        'Render all the element from instance of view'
        pass

    @abstractmethod
    def show(sef) -> None:
        'Show plots'
