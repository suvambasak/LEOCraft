import time

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_2D import SatView2D

start_time = time.perf_counter()


leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        'dataset/ground_stations/ground_stations_cities_sorted_by_estimated_2025_pop_top_100.csv'
        # 'dataset/ground_stations/ground_stations_cities_sorted_by_estimated_2025_pop_top_1000.csv'
    )
)

# Adding Shells
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

# Starlink Shell 2
leo_con.add_shells(
    PlusGridShell(
        id=1,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=540000.0,
        inclination_degree=53.2,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)

# Starlink Shell 3
leo_con.add_shells(
    PlusGridShell(
        id=2,
        orbits=36,
        sat_per_orbit=20,
        altitude_m=570000.0,
        inclination_degree=70.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)


leo_con.set_time(minute=20)  # Time passed after epoch
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()

leo_con.generate_routes()


view = SatView2D(leo_con)
# view.add_ground_stations('G-0', 'G-1', 'G-2', 'G-3')
# view.add_satellites('S0-0', 'S0-1', 'S0-2', 'S0-3', 'S0-26')
# view.add_coverages('S0-0', 'S0-1', 'S0-40', 'S0-31', 'S0-30')
# view.add_GSLs('G-1', 'G-2')
# view.add_ISLs((('S0-0', 'S0-1'), ('S0-0', 'S0-25'), ('S0-0', 'S0-24')))
view.add_routes('G-0_G-1', 'G-1_G-2', 'G-2_G-3', 'G-30_G-33', k=1)

for sat in leo_con.routes['G-2_G-3'][0][1:-1]:
    view.add_coverages(sat)

# view.add_all_ground_stations()
# view.add_all_satellites()
# view.add_all_coverages()
# view.add_all_GSLs()
# view.add_all_ISLs()
# view.add_all_routes()

view.build()
view.show()

view.export_html()


end_time = time.perf_counter()
print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
