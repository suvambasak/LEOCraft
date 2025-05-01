
'''
Generate ISls usage visualization
Figure. 28 in the paper
'''

import math

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D


class CustomSatView3D(SatView3D):

    _DEFAULT_WIDTH = 5

    def setup_usage_scale(self, path_selection: dict[str, dict[int, float]]) -> None:

        self.__ISL_usage_records = dict()
        for flow, flow_units_per_route_dict in path_selection.items():
            # print(flow, flow_units_per_route_dict)

            for route_id, flow_unit in flow_units_per_route_dict.items():
                # print(type(route_id))
                # print(route_id, flow_unit)
                # print(leo_con.routes[flow][route_id])

                for hop_id in range(1, len(leo_con.routes[flow][route_id])-2):

                    if leo_con.routes[flow][route_id][hop_id] < leo_con.routes[flow][route_id][hop_id+1]:
                        __key = f"{leo_con.routes[flow][route_id][hop_id]}_{
                            leo_con.routes[flow][route_id][hop_id+1]}"
                    else:
                        __key = f"{leo_con.routes[flow][route_id][hop_id+1]
                                   }_{leo_con.routes[flow][route_id][hop_id]}"

                    if __key in self.__ISL_usage_records:
                        self.__ISL_usage_records[__key] += flow_unit
                    else:
                        self.__ISL_usage_records[__key] = flow_unit

        self.__max_usage = math.ceil(max(self.__ISL_usage_records.values()))

    def get_color(self, hop_a: str, hop_b: str) -> str:

        __key = f"{hop_a}_{hop_b}" if hop_a < hop_b else f"{hop_b}_{hop_a}"
        __load = self.__ISL_usage_records[__key] if __key in self.__ISL_usage_records else 0

        __std_usage = __load/self.__max_usage*100

        if __std_usage <= 0:
            return "rgb(209, 209, 209)"
        elif __std_usage <= 20:
            return "rgb(157, 250, 157)"
        elif __std_usage <= 60:
            return "rgb(247, 199, 104)"
        elif __std_usage <= 80:
            return "rgb(247, 89, 89)"
        else:
            return "rgb(129, 5, 252)"


leo_con = LEOConstellation()
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        GroundStationAtCities.TOP_100
        # GroundStationAtCities.COUNTRY_CAPITALS
    )
)
leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=72,
        sat_per_orbit=22,
        # orbits=30,
        # sat_per_orbit=30,
        altitude_m=1000.0*550,
        inclination_degree=53.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)

leo_con.set_time(minute=0)  # Time passed after epoch
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()
leo_con.generate_routes()

th = Throughput(
    leo_con,
    InternetTrafficAcrossCities.ONLY_POP_100
    # InternetTrafficAcrossCities.POP_GDP_100
    # InternetTrafficAcrossCities.ONLY_POP_1000
    # InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
)
th.build()
th.compute()


view = CustomSatView3D(leo_con)
view.setup_usage_scale(th.path_selection)


# view.add_satellites('S0-0')
view.add_all_satellites()
view.add_all_ISLs()
view.add_all_ground_stations()
# view.add_all_routes()

view.build()
view.show()
