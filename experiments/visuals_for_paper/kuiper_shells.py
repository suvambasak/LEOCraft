

'''
Generate multi shell constellation design of kuiper, Starlink, Telesat, OneWeb
Figure. 1 (b) and Figure. 24 in the paper.


Enable this code in view.py: def get_color(self, hop_a: str, hop_b: str) -> str:
# __color_code = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)']
# shell_id, _ = LEOSatelliteTopology.decode_sat_name(hop_a)
# return __color_code[shell_id]
'''


from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D


class CustomSatRawView3D(SatRawView3D):
    def get_color(self, hop_a: str, hop_b: str) -> str:
        '''GSL and ISL link line thickness

        Parameters
        --------
        hop_a: str
            First hop name
        hop_b: str
            Second hop name

        Returns
        -------
        str
            Color code
        '''

        __color_code = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)']
        shell_id, _ = LEOSatelliteTopology.decode_sat_name(hop_a)
        return __color_code[shell_id]

###############################################################
# Kuiper
###############################################################


# leo_con = LEOConstellation('Kuiper')
# leo_con.v.verbose = True
# leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

# leo_con.add_shells(PlusGridShell(
#     id=0,
#     orbits=34,
#     sat_per_orbit=34,
#     altitude_m=1500000.0,
#     inclination_degree=51.9,
#     angle_of_elevation_degree=35.0,
#     phase_offset=0.0
# ))
# leo_con.add_shells(PlusGridShell(
#     id=1,
#     orbits=36,
#     sat_per_orbit=36,
#     altitude_m=1000000.0,
#     inclination_degree=42.0,
#     angle_of_elevation_degree=35.0,
#     phase_offset=0.0
# ))

# leo_con.add_shells(PlusGridShell(
#     id=2,
#     orbits=28,
#     sat_per_orbit=28,
#     altitude_m=500000.0,
#     inclination_degree=33.0,
#     angle_of_elevation_degree=35.0,
#     phase_offset=0.0
# ))

###############################################################


###############################################################
# Starlink
###############################################################

leo_con = LEOConstellation('Starlink Gen1')
leo_con.v.verbose = True
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

leo_con.add_shells(PlusGridShell(
    id=0,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=500000.0,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
))

leo_con.add_shells(PlusGridShell(
    id=1,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=1000000.0,
    inclination_degree=53.2,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
))

leo_con.add_shells(PlusGridShell(
    id=2,
    orbits=36,
    sat_per_orbit=20,
    altitude_m=1500000.0,
    inclination_degree=70.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
))

###############################################################


###############################################################
# Telesat
###############################################################

# leo_con = LEOConstellation('Telesat')
# leo_con.v.verbose = True
# leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

# leo_con.add_shells(PlusGridShell(
#     id=0,
#     orbits=27,
#     sat_per_orbit=13,
#     altitude_m=1000000.0,
#     inclination_degree=98.98,
#     angle_of_elevation_degree=40.0,  # reducde for speed
#     phase_offset=50.0
# ))

# leo_con.add_shells(PlusGridShell(
#     id=1,
#     orbits=40,
#     sat_per_orbit=33,
#     altitude_m=1500000.0,
#     inclination_degree=50.88,
#     angle_of_elevation_degree=40.0,  # reducde for speed
#     phase_offset=50.0
# ))

###############################################################


###############################################################
# OneWeb
###############################################################

# leo_con = LEOConstellation('OneWeb')
# leo_con.v.verbose = True
# leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

# leo_con.add_shells(PlusGridShell(
#     id=0,
#     orbits=36,
#     sat_per_orbit=49,
#     altitude_m=1200000.0,
#     inclination_degree=87.9,
#     angle_of_elevation_degree=50.0,  # reducde for speed
#     phase_offset=50.0
# ))

# leo_con.add_shells(PlusGridShell(
#     id=1,
#     orbits=32,
#     sat_per_orbit=720,
#     altitude_m=1200000.0,
#     inclination_degree=40.0,
#     angle_of_elevation_degree=50.0,  # reducde for speed
#     phase_offset=50.0
# ))

# leo_con.add_shells(PlusGridShell(
#     id=2,
#     orbits=32,
#     sat_per_orbit=720,
#     altitude_m=1200000.0,
#     inclination_degree=55.0,
#     angle_of_elevation_degree=50.0,  # reducde for speed
#     phase_offset=50.0
# ))

###############################################################

leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


view = CustomSatRawView3D(
    leo_con,

    lat=16.80528,
    long=96.15611,
    elevation_m=95000
)


view._DEFAULT_SAT_SIZE = 10
view._shell_colors = ['rgb(0, 0, 255)', 'rgb(0, 255, 0)', 'rgb(255, 0, 0)']


view.add_all_satellites()
view.add_all_ISLs()
view._sat = sorted(list(view._sat))


view.build()
# view.show()

# view.export_html('docs/html/kuiper_shells.html')
view.export_html('docs/html/starlink_shells.html')
# view.export_html('docs/html/telesat_shells.html')
# view.export_png()
