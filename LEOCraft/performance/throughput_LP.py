import json
import time

import gurobipy as gp
from gurobipy import GRB

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.performance import Performance
from LEOCraft.performance.route_classifier.flow_classifier import \
    FlowClassifier


class ThroughputLP(Performance):
    """
    Implements Performance for computing LEO constellation throughput 
    using multi-commodity flow (MCNF) across ground stations using linear program
    """

    def __init__(self, leo_con: Constellation, tm_path: str) -> None:
        super().__init__(leo_con)
        self.traffic_metrics = tm_path

        self.throughput_Gbps: float
        self.total_accommodated_flow: float
        self.NS_selt: float
        self.EW_selt: float
        self.NESW_selt: float
        self.HG_selt: float
        self.LG_selt: float

    def build(self) -> None:
        self.v.nl()
        self.v.log('Building throughput...')
        self.v.rlog('Processing traffic_metrics...')
        self._process_traffic_metrics()
        self.v.rlog('Connecting all ground stations...')
        for gid, _ in enumerate(self.leo_con.ground_stations.terminals):
            self.leo_con.connect_ground_station(
                self.leo_con.ground_stations.encode_name(gid)
            )
        self.v.clr()

    def compute(self) -> None:
        self.v.log('Computing throughput...')
        self._solve_linear_program()
        self._extract_path_selection()

        # Analytics
        self._compute_total_accommodated_flow()
        self._compute_total_route_selection()

    def _process_traffic_metrics(self) -> None:
        '''Create demand_metrics merging two up and down flows from the JSON file

        i.e. Creates one flow of (G-X_G-Y + G-Y_G-X)
        '''

        with open(self.traffic_metrics) as json_file:
            content = json.loads(json_file.read())

        self.demand_metrics = dict()

        for s in range(len(self.leo_con.ground_stations.terminals)):
            for d in range(s+1, len(self.leo_con.ground_stations.terminals)):
                s_gs_name = self.leo_con.ground_stations.encode_name(s)
                d_gs_name = self.leo_con.ground_stations.encode_name(d)
                outgoing_key = f"{s_gs_name}_{d_gs_name}"
                incoming_key = f"{d_gs_name}_{s_gs_name}"

                self.demand_metrics[outgoing_key] = content[incoming_key] + \
                    content[outgoing_key]

    def _solve_linear_program(self) -> None:
        'Form a LP and solve for the throughput using gurobi package'

        # Gurobi LP/ILP formation
        self.v.rlog('LP formation...')
        flows = self.leo_con.routes.keys()
        links = self.leo_con.link_load.keys()

        self.model = gp.Model("ThroughputLP")

        # Variables
        flow_via_route = self.model.addVars(
            flows, self.leo_con.k,
            vtype=GRB.CONTINUOUS,
            lb=0, ub=1,
            name="R"
        )

        # Objective function
        obj_fun = gp.quicksum(
            flow_via_route.sum(flow, '*') * self.demand_metrics[flow] for flow in flows
        )
        self.model.setObjective(obj_fun, GRB.MAXIMIZE)

        # Route selection constraints
        # Selecting path(s) out of K path
        self.model.addConstrs(
            (flow_via_route.sum(flow, '*') <= 1 for flow in flows), name="select_path"
        )

        # Link capacity constraints
        # Flow through a link must be less than equal to the capacity of the link
        for link in links:
            self.model.addConstr(
                (
                    gp.quicksum(
                        flow_via_route[flow, index] * self.demand_metrics[flow] for flow, index in self.leo_con.link_load[link]
                    ) <= self.leo_con.link_capacity(link[0], link[1])
                ),
                name=f"link_cap_ub_{link[0]}_{link[1]}"
            )

        self.model.setParam("OutputFlag", False)

        self.v.rlog(f"Optimizing... ")
        start_time = time.perf_counter()
        self.model.optimize()
        end_time = time.perf_counter()
        self.v.clr()

        self.throughput_Gbps = round(self.model.objVal, 3)
        self.v.log(f'Optimized in: {round((end_time-start_time)/60, 2)}m')
        self.v.log(f'Throughput:\t{self.throughput_Gbps} Gbps')

    def _extract_path_selection(self) -> None:
        'Process the output of LP solver to extract selected routes'

        self.path_selection = {}

        # Extract seleted paths from gurobi model
        for v in self.model.getVars():
            if v.x:
                key = v.varName[2:-1].split(',')
                flow = key[0]
                path = int(key[1])

                if flow not in self.path_selection.keys():
                    self.path_selection[flow] = dict()
                self.path_selection[flow][path] = v.x

    def export_path_selection(self, prefix_path: str = '.') -> str:
        '''Writes path selection into a JSON file

        Returns
        --------
        str
            Path of the written file
        '''

        # Get the directory of time delta
        dir = self._create_export_dir(prefix_path)

        # Write inside time delta
        filename = f'{dir}/path_selection.json'
        with open(filename, 'w') as json_file:
            json_file.write(json.dumps(self.path_selection))

        return filename

    def export_LP_model(self, prefix_path: str = '.') -> str:
        '''Writes LP into a file

        Returns
        --------
        str
            Path of the written file
        '''

        # Get the directory of time delta
        dir = self._create_export_dir(prefix_path)

        # Write inside time delta
        filename = f'{dir}/{self.__class__.__name__}.lp'
        self.model.write(filename)

        return filename

    def _compute_total_accommodated_flow(self) -> None:
        'Calculate % of flow accommodated by the constellation'

        total_flow = len(self.demand_metrics.keys())
        accommodated_flow = 0.0

        for _, rindex_flow_fraction in self.path_selection.items():
            accommodated_flow += sum(rindex_flow_fraction.values())

        self.total_accommodated_flow = (accommodated_flow/total_flow)*100

        self.v.log(f'''Total accommodated flow:\t{
                   round(self.total_accommodated_flow, 3)} %''')

    def _compute_total_route_selection(self) -> None:
        'Calculate % of routes end to end routes selected of each flow class'

        rcategories = FlowClassifier(self.leo_con)
        rcategories.classify()

        self.NS_selt = round(self._count_route_selection(
            rcategories.route_north_south)/(len(rcategories.route_north_south)*self.leo_con.k)*100, 3)
        self.v.log(f'NS path selection:\t{self.NS_selt} %')

        self.EW_selt = round(self._count_route_selection(
            rcategories.route_east_west)/(len(rcategories.route_east_west)*self.leo_con.k)*100, 3)
        self.v.log(f'EW path selection:\t{self.EW_selt} %')

        self.NESW_selt = round(self._count_route_selection(rcategories.route_northeast_southwest)/(
            len(rcategories.route_northeast_southwest)*self.leo_con.k)*100, 3)
        self.v.log(f'NESW path selection:\t{self.NESW_selt} %')

        self.HG_selt = round(self._count_route_selection(
            rcategories.route_high_geodesic)/(len(rcategories.route_high_geodesic)*self.leo_con.k)*100, 3)
        self.v.log(f'HG path selection:\t{self.HG_selt} %')

        self.LG_selt = round(self._count_route_selection(
            rcategories.route_low_geodesic)/(len(rcategories.route_low_geodesic)*self.leo_con.k)*100, 3)
        self.v.log(f'LG path selection:\t{self.LG_selt} %')

    def _count_route_selection(self, flows: set[str]) -> int:
        '''Counts the number of path selected from a given flow category. Works as helper method of _compute_total_route_selection

        Parameters
        -------
        flows: set[str]
            Set of flows

        Returns
        ------
        int
            Selected path count
        '''

        counter = 0
        for flow in flows:
            route_selection = self.path_selection.get(flow)
            if route_selection:
                counter += len(route_selection.keys())

        return counter
