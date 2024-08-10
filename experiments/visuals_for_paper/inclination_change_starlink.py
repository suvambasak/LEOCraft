
'''View inclination change of Starlink'''

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D

leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
leo_con.add_shells(PlusGridShell(
    id=0,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=550000.0,
    inclination_degree=5.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
))


leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


view = SatView3D(leo_con)
view._DEFAULT_GS_SIZE = 17
view.add_all_ground_stations()
view.add_all_satellites()
view.add_all_GSLs()
view.add_all_ISLs()
view.build()
view.show()
