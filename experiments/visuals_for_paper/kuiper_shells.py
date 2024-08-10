

'''

Generate multi shell constellation design of kuiper


Enable this code in view.py: def get_color(self, hop_a: str, hop_b: str) -> str:
# __color_code = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)']
# shell_id, _ = LEOSatelliteTopology.decode_sat_name(hop_a)
# return __color_code[shell_id]
'''


from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D


leo_con = LEOConstellation('Kuiper')
leo_con.v.verbose = True
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

leo_con.add_shells(PlusGridShell(
    id=0,
    orbits=34,
    sat_per_orbit=34,
    altitude_m=1500000.0,
    inclination_degree=51.9,
    angle_of_elevation_degree=35.0,
    phase_offset=0.0
))
leo_con.add_shells(PlusGridShell(
    id=1,
    orbits=36,
    sat_per_orbit=36,
    altitude_m=1000000.0,
    inclination_degree=42.0,
    angle_of_elevation_degree=35.0,
    phase_offset=0.0
))

leo_con.add_shells(PlusGridShell(
    id=2,
    orbits=28,
    sat_per_orbit=28,
    altitude_m=500000.0,
    inclination_degree=33.0,
    angle_of_elevation_degree=35.0,
    phase_offset=0.0
))


leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


view = SatRawView3D(
    leo_con,

    lat=16.80528,
    long=96.15611,
    elevation_m=95000
)


view._DEFAULT_SAT_SIZE = 15
view._shell_colors = ['rgb(0, 0, 255)', 'rgb(0, 255, 0)', 'rgb(255, 0, 0)']


view.add_all_satellites()
view.add_all_ISLs()
view._sat = sorted(list(view._sat))


view.build()
view.show()

# view.export_html()
# view.export_png()
