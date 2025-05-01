'''
This example shows how to render evolution of a LEO constellation network fame by frame
Which allows to visualize:
- Network topology changes
- Coverage changes
- Route changes
- Handover between satellites and ground stations
'''

import time

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import k_shortest_paths
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D
from LEOCraft.visuals.sat_view_3D import SatView3D

start_time = time.perf_counter()


for t in range(0, 50, 5):
    leo_con = LEOConstellation('Starlink')
    leo_con.v.verbose = True
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
            # GroundStationAtCities.TOP_1000
        )
    )

    # Starlink Shell 1
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=72,
            sat_per_orbit=22,
            altitude_m=550000.0,
            inclination_degree=53.0,
            angle_of_elevation_degree=25.0,
            phase_offset=50.0
        )
    )

    # # Starlink Shell 2
    # leo_con.add_shells(
    #     PlusGridShell(
    #         id=1,
    #         orbits=72,
    #         sat_per_orbit=22,
    #         altitude_m=540000.0,
    #         inclination_degree=53.2,
    #         angle_of_elevation_degree=25.0,
    #         phase_offset=50.0
    #     )
    # )

    # # Starlink Shell 3
    # leo_con.add_shells(
    #     PlusGridShell(
    #         id=2,
    #         orbits=36,
    #         sat_per_orbit=20,
    #         altitude_m=570000.0,
    #         inclination_degree=70.0,
    #         angle_of_elevation_degree=25.0,
    #         phase_offset=50.0
    #     )
    # )

    leo_con.set_time(second=t)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    # Generate all the routes
    # leo_con.generate_routes()

    # Generate routes from Hyderabad to Tokyo
    src = 'G-0'
    dst = 'G-36'

    leo_con.connect_ground_station(src, dst)
    compute_status, flow, k_path = k_shortest_paths(
        leo_con.sat_net_graph, src, dst, k=20
    )

    leo_con.routes = dict()
    leo_con.link_load = dict()
    leo_con.no_path_found = set()
    leo_con.k_path_not_found = set()

    leo_con._add_route(compute_status, flow, k_path)

    # Set the view coordinates
    # sat_info = leo_con.sat_info('S0-1')  # Track a satellite

    # # With GEO
    # view = SatView3D(
    #     leo_con,

    #     lat=16.80528, long=96.15611,

    #     # lat=sat_info.nadir_latitude_deg,
    #     # long=sat_info.nadir_longitude_deg,

    #     title=f'Time: {t}s'
    # )

    # With RAW 3D
    view = SatRawView3D(
        leo_con,

        lat=16.0, long=85.0,
        elevation_m=560000.0,

        # lat=sat_info.nadir_latitude_deg,
        # long=sat_info.nadir_longitude_deg,

        title=f'Time: {t}s'
    )
    view.add_coverages(k_path[0][1], k_path[0][-2])

    view.add_routes(flow, k=1)
    view.add_all_satellites()
    view.build()
    # view.show()
    # File name with 4 digit time stamp
    view.export_png(f'{str(t).zfill(4)}.png')

    end_time = time.perf_counter()
    print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
