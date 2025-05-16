
'''
Generate different class of routes
- north south routes
- east west routes
- northeast southwest routes
- high geodesic route

Figure. 2 in the paper
'''

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D
from LEOCraft.performance.route_classifier.basic_classifier import BasicClassifier


leo_con = LEOConstellation()
leo_con.v.verbose = True
leo_con.k = 1
leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=30,
        sat_per_orbit=30,
        altitude_m=550000.0,
        inclination_degree=90.0,
        angle_of_elevation_degree=25.0,
        phase_offset=0.0
    )
)
# leo_con.set_time(minute=5)
leo_con.set_time()
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()
leo_con.generate_routes()


flow_classifier = BasicClassifier(leo_con)
flow_classifier.classify()

# route_category = flow_classifier.route_north_south
# route_category = flow_classifier.route_east_west
# route_category = flow_classifier.route_northeast_southwest

# flow_classifier.route_high_geodesic
route_category = set()
route_category.add('G-15_G-18')
route_category.add('G-9_G-28')


# Pre processing: removing the GSLs are not in routes
# ---------------------
present: dict[int, set[str]] = dict()
for flow in route_category:
    sgid, s_sat_name = int(leo_con.routes[flow][0][0].split(
        '-')[-1]), leo_con.routes[flow][0][1]
    dgid, d_sat_name = int(
        leo_con.routes[flow][0][-1].split('-')[-1]), leo_con.routes[flow][0][-2]

    if sgid not in present:
        present[sgid] = set()
    present[sgid].add(s_sat_name)

    if dgid not in present:
        present[dgid] = set()
    present[dgid].add(d_sat_name)

for gid in range(len(leo_con.gsls)):
    valid_gsl_set = set()
    for gsl_info in leo_con.gsls[gid]:
        sat, _ = gsl_info
        if gid in present and sat in present[gid]:
            valid_gsl_set.add(gsl_info)
    leo_con.gsls[gid] = valid_gsl_set
# --------------------


# view = SatView3D(leo_con, "Route: North East to South West")
# view = SatView3D(leo_con, "Route: East to West")
# view = SatView3D(leo_con, "Route: North to South")
view = SatView3D(leo_con, "Route: High Geodesic Distance")
view._DEFAULT_SAT_SIZE = 12
view._DEFAULT_GS_SIZE = 15

view.add_all_satellites()
for flow in route_category:
    view.add_routes(flow)

view.build()

# view.show()
# view.export_html(f'docs/html/NESW.html')
# view.export_html(f'docs/html/EW.html')
# view.export_html(f'docs/html/NS.html')
view.export_html(f'docs/html/HG.html')
