

'''Generate coverage cone of satellites with e=30.0 and e=40.0'''


from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D


leo_con = LEOConstellation('Test')
leo_con.v.verbose = True
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

leo_con.add_shells(PlusGridShell(
    id=0,
    orbits=20,
    sat_per_orbit=20,
    altitude_m=2000000.0,
    inclination_degree=90.0,
    angle_of_elevation_degree=40.0,
    phase_offset=0.0
))
leo_con.add_shells(PlusGridShell(
    id=1,
    orbits=20,
    sat_per_orbit=20,
    altitude_m=2000000.0,
    inclination_degree=90.0,
    angle_of_elevation_degree=30.0,
    phase_offset=0.0
))

leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()

print(round(leo_con.shells[0].satellites[1].coverage_cone_radius_m()/1000, 1))
print(round(leo_con.shells[1].satellites[1].coverage_cone_radius_m()/1000, 1))


view = SatRawView3D(
    leo_con,

    lat=16.80528,
    long=96.15611,
    elevation_m=95000,
    globe_visibility=False
)

view.add_satellites('S0-1')
view.add_coverages('S0-1', 'S1-1')

view.build()
view.show()

# view.export_html()
# view.export_png()
