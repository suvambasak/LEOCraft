
'''View path diversity of high geodesig distance routes'''

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import k_shortest_paths
from LEOCraft.visuals.sat_view_3D import SatView3D

leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True

leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
leo_con.add_shells(PlusGridShell(
    id=0,


    orbits=144,
    sat_per_orbit=11,
    phase_offset=50.0,

    # orbits=144,
    # sat_per_orbit=11,
    # phase_offset=0.0,

    # orbits=48,
    # sat_per_orbit=33,
    # phase_offset=50.0,


    altitude_m=550000.0,
    inclination_degree=38.6,
    angle_of_elevation_degree=12.1
))


leo_con.set_time(minute=5)
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


# high geodesic distance route
src = 'G-45'
dst = 'G-83'

leo_con.routes = dict()
leo_con.link_load = dict()
leo_con.no_path_found = set()
leo_con.k_path_not_found = set()


leo_con.connect_ground_station(src, dst)
compute_status, flow, k_path = k_shortest_paths(
    leo_con.sat_net_graph, src, dst, k=leo_con.k
)
leo_con._add_route(compute_status, flow, k_path)
leo_con.disconnect_ground_station(src, dst)


present: dict[int, set[str]] = dict()
for r in range(leo_con.k):
    sgid = int(leo_con.routes[flow][r][0].split('-')[-1])
    dgid = int(leo_con.routes[flow][r][-1].split('-')[-1])
    s_sat_name = leo_con.routes[flow][r][1]
    d_sat_name = leo_con.routes[flow][r][-2]

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


view = SatView3D(leo_con, lat=20.0, long=-170.0)
view.add_routes(flow)
view.add_all_satellites()
view.build()
view.show()
