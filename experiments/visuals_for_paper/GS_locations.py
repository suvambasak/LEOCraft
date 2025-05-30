
'''
View the 100 ground stations location
Figure. 7 (a) in the paper
'''


from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_2D import SatView2D

leo_con = LEOConstellation()
leo_con.v.verbose = True
# leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
# leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_1000))
leo_con.add_ground_stations(GroundStation(
    GroundStationAtCities.COUNTRY_CAPITALS
))
leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=72,
        sat_per_orbit=22,
        altitude_m=1000.0*600,
        inclination_degree=53.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    )
)

leo_con.set_time(minute=0)  # Time passed after epoch
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


view = SatView2D(leo_con)
view.add_all_ground_stations()

view.build()
# view.show()

# view.export_html('docs/html/GS_locations_100.html')
# view.export_html('docs/html/GS_locations_1000.html')
view.export_html('docs/html/GS_locations_CAPITALS.html')
