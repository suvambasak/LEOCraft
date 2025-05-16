
'''
Coverage change with shell altitude.
Figure. 4 in the paper
'''


from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_2D import SatView2D

leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=72,
        sat_per_orbit=22,
        # altitude_m=1000.0*600,
        altitude_m=1000.0*300,
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
view.add_all_satellites()
view.add_all_coverages()

view.build()
# view.show()

# view.export_html('docs/html/starlink_coverage_h600.html')
view.export_html('docs/html/starlink_coverage_h300.html')
