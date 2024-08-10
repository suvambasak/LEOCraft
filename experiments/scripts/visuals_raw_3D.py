import time

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import k_shortest_paths
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D

start_time = time.perf_counter()


leo_con = LEOConstellation('Kuiper')
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        GroundStationAtCities.TOP_100
        # GroundStationAtCities.TOP_1000
    )
)

# Adding Shells
# Starlink Shell 1
leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=20,
        sat_per_orbit=20,
        altitude_m=2000000.0,
        inclination_degree=90.0,
        angle_of_elevation_degree=40.0,
        phase_offset=0.0
    )
)
leo_con.add_shells(
    PlusGridShell(
        id=1,
        orbits=20,
        sat_per_orbit=20,
        altitude_m=2000000.0,
        inclination_degree=90.0,
        angle_of_elevation_degree=30.0,
        phase_offset=0.0
    )
)


# leo_con.add_shells(
#     PlusGridShell(
#         id=0,
#         orbits=34,
#         sat_per_orbit=34,
#         altitude_m=1500000.0,
#         inclination_degree=51.9,
#         angle_of_elevation_degree=35.0,
#         phase_offset=0.0
#     )
# )
# leo_con.add_shells(
#     PlusGridShell(
#         id=1,
#         orbits=36,
#         sat_per_orbit=36,
#         altitude_m=1000000.0,
#         inclination_degree=42.0,
#         angle_of_elevation_degree=35.0,
#         phase_offset=0.0
#     )
# )

# leo_con.add_shells(
#     PlusGridShell(
#         id=2,
#         orbits=28,
#         sat_per_orbit=28,
#         altitude_m=500000.0,
#         inclination_degree=33.0,
#         angle_of_elevation_degree=35.0,
#         phase_offset=0.0
#     )
# )


# leo_con.set_time(minute=20)  # Time passed after epoch
leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()

print(round(leo_con.shells[0].satellites[1].coverage_cone_radius_m()/1000, 1))
print(round(leo_con.shells[1].satellites[1].coverage_cone_radius_m()/1000, 1))

# # Generates all the routes
# leo_con.generate_routes()


# -----------------------------------
# Need to generate a specific routes
# -----------------------------------
# src = 'G-28'
# dst = 'G-20'
# leo_con.connect_ground_station(src, dst)
# compute_status, flow, k_path = k_shortest_paths(
#     leo_con.sat_net_graph, src, dst, k=20
# )

# leo_con.routes = dict()
# leo_con.link_load = dict()
# leo_con.no_path_found = set()
# leo_con.k_path_not_found = set()

# leo_con._add_route(compute_status, flow, k_path)


view = SatRawView3D(
    leo_con,

    lat=16.80528,
    long=96.15611,
    elevation_m=95000,
    globe_visibility=False
)

# # View selected components
# view.add_ground_stations('G-0', 'G-1', 'G-2', 'G-3')
# view.add_satellites('S0-0', 'S0-1', 'S0-2', 'S0-3', 'S0-26')
# view.add_coverages(
#     k_path[0][1], k_path[0][-2],
#     k_path[1][1], k_path[1][-2],
#     k_path[3][1], k_path[3][-2],
#     k_path[4][1], k_path[4][-2],
#     k_path[5][1], k_path[5][-2]
# )
# view.add_GSLs('G-1', 'G-2')
# view.add_ISLs((('S0-0', 'S0-1'), ('S0-0', 'S0-25'), ('S0-0', 'S0-24')))
# view.add_routes('G-0_G-1', 'G-1_G-2', 'G-2_G-3', 'G-30_G-33', k=1)

# view.add_routes(flow)  # Need to generate a specific routes


# View all components
# view.add_all_ground_stations()
# view.add_all_satellites()
# view.add_all_coverages()
# view.add_all_GSLs()
# view.add_all_ISLs()
# view.add_all_routes()

# for i in range(33):
#     view.add_ISLs(((f'S0-{i}', f'S0-{i+1}'),))
# view.add_ISLs(((f'S0-{0}', f'S0-{33}'),))
# for i in range(35):
#     view.add_ISLs(((f'S1-{i}', f'S1-{i+1}'),))
# view.add_ISLs(((f'S1-{0}', f'S1-{35}'),))
# for i in range(27):
#     view.add_ISLs(((f'S2-{i}', f'S2-{i+1}'),))
# view.add_ISLs(((f'S2-{0}', f'S2-{27}'),))

view.add_satellites('S0-1')
view.add_coverages('S0-1', 'S1-1')

view.build()
view.show()

view.export_html()
view.export_png()


end_time = time.perf_counter()
print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
