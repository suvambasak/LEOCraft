
'''View all type of routes with AoE and inclination'''

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import k_shortest_paths
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D
from LEOCraft.visuals.sat_view_2D import SatView2D
from LEOCraft.visuals.sat_view_3D import SatView3D

leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True
leo_con.k = 1

leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
leo_con.add_shells(PlusGridShell(
    id=0,
    orbits=72,
    sat_per_orbit=22,
    # altitude_m=1000.0*550,
    altitude_m=1000.0*1000,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
))
# leo_con.set_time(minute=3)
leo_con.set_time(second=100)
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()
# leo_con.generate_routes()


flows: dict[str, str] = dict()

src = 'G-0'
dst = 'G-28'

leo_con.routes = dict()
leo_con.link_load = dict()
leo_con.no_path_found = set()
leo_con.k_path_not_found = set()


leo_con.connect_ground_station(src, dst)
compute_status, flow, k_path = k_shortest_paths(
    leo_con.sat_net_graph, src, dst, k=leo_con.k
)
leo_con.disconnect_ground_station(src, dst)
leo_con._add_route(compute_status, flow, k_path)

present: dict[int, set[str]] = dict()
for flow in leo_con.routes.keys():
    sgid = int(leo_con.routes[flow][0][0].split('-')[-1])
    dgid = int(leo_con.routes[flow][0][-1].split('-')[-1])
    s_sat_name = leo_con.routes[flow][0][1]
    d_sat_name = leo_con.routes[flow][0][-2]

    # print(sgid, s_sat_name, d_sat_name, dgid)

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


# view = SatRawView3D(leo_con)
# view._THICK_WIDTH = 10
# view.add_routes(flow)
# view.add_coverages(leo_con.routes[flow][0][1])
# view.add_coverages(leo_con.routes[flow][0][-2])
# view.add_all_satellites()
# view.build()
# view.show()


view = SatView2D(leo_con)
view._COVERAGE_OPACITY = 0.5
view._THICK_WIDTH = 10
view._DEFAULT_SAT_SIZE = 23
view.add_routes(flow)
view.add_coverages(leo_con.routes[flow][0][1])
view.add_coverages(leo_con.routes[flow][0][-2])
view.add_all_satellites()
view.build()
view.export_html('export1000.html')


# view = SatView3D(leo_con, lat=27.468683, long=113.189875)
# view._THICK_WIDTH = 10
# view.add_routes(flow)
# view.add_all_satellites()
# view.build()
# view.export_png('path_100.png')
