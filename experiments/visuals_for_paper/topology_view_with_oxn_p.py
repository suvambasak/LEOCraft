
'''
View topology of the shell with o, n, and p
Figure. 11 in the paper
'''

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D

# orbits = 72
# sat_per_orbit = 22
# phase_offset = 50.0

# orbits = 22
# sat_per_orbit = 72
# phase_offset = 50.0

# orbits = 44
# sat_per_orbit = 36
# phase_offset = 50.0

orbits = 44
sat_per_orbit = 36
phase_offset = 0.0

FNAME = f'o{orbits}_n{sat_per_orbit}_p{phase_offset}.html'


leo_con = LEOConstellation(
    f'Starlink : orbits={orbits}, sat_per_orbit={sat_per_orbit}, phase_offset={round(phase_offset)}'
)
leo_con.v.verbose = True

leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
leo_con.add_shells(
    PlusGridShell(
        id=0,

        orbits=orbits,
        sat_per_orbit=sat_per_orbit,
        phase_offset=phase_offset,

        altitude_m=550000.0,
        inclination_degree=90.0,
        angle_of_elevation_degree=25.0,


    )
)
leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


view = SatView3D(leo_con, lat=7.0, long=75.0)
view.add_all_ISLs()
view.add_all_satellites()
view.build()

# view.show()

view.export_html(f'docs/html/{FNAME}')

print(
    f'orbits={orbits}, sat_per_orbit={sat_per_orbit}, phase_offset={phase_offset}'
)
