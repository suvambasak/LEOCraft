import time

import networkx

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import CSV_logger, k_shortest_paths


def compute_at_epoch(size: int, time_s: int) -> None:

    leo_con = LEOConstellation('LEOCON')
    leo_con.k = 1
    leo_con.v.verbose = False
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
            # GroundStationAtCities.TOP_1000
        )
    )

    leo_con.add_shells(
        PlusGridShell(
            id=0,

            orbits=size,
            sat_per_orbit=size,

            altitude_m=1000*1000,
            inclination_degree=90.0,
            angle_of_elevation_degree=30.0,
            phase_offset=50.0
        )
    )

    leo_con.set_time(second=time_s)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()
    # leo_con.generate_routes()

    for sgid in range(50):
        src = f"G-{sgid}"
        dst = f"G-{sgid+50}"
        try:
            leo_con.connect_ground_station(src, dst)
            compute_status, flow, k_path = k_shortest_paths(
                leo_con.sat_net_graph, src, dst, k=1
            )

            path = k_path[-1]
            route_length_m = 0

            for hop_id in range(len(path)-1):
                # print(path[hop_id], path[hop_id+1])
                route_length_m += leo_con.link_length(
                    path[hop_id], path[hop_id+1])

            #  Speed of light: 299792458 m/s
            # RTT_ms = (2000*route_length_m)/299792458

        except networkx.exception.NodeNotFound:
            print(f" > sgid: {sgid} Failed.")

    print(f" > times_s {time_s}s")


if __name__ == '__main__':

    for size in range(70, 80, 5):

        print(f'-----------------------------------------------: {size}')
        start_time = time.perf_counter()
        for time_s in range(200):
            compute_at_epoch(size, time_s)
        end_time = time.perf_counter()
        print(f'-----------------------------------------------: {size}')

        print(f'''Time: {round((end_time-start_time)/60, 2)}m ''')

        CSV_logger(
            {
                'o': size,
                'n': size,
                'time_s': end_time-start_time
            },

            'LEOCraftRunTime.csv'
        )
