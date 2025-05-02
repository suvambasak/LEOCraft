
'''
This script computes the RTT between three ground station pairs 
(Delhi to New-york, Moscow to Paris, Tokyo to Sydney) over 
Starlink, Kuiper, and Telesat LEO constellation.

For same experiement with Hypatia checkout [1]:
1. pingKuiper.py
2. pingStarlink.py
3. pingTelesat.py


Generated dataset is used to producde the Figures. 17 in the paper.

Reference:
1. https://github.com/suvambasak/hypatia/tree/master/evaluation

'''

import networkx

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.utilities import CSV_logger, k_shortest_paths

# SOURCE_GS = 'G-1'
# DESTINATION_GS = 'G-9'
# RTT_CSV = 'kuiper_k1/ping_delhi_to_new-york_rtt.csv'
# PATH_CHANGE_CSV = 'kuiper_k1/change_delhi_to_new-york_path.csv'

# SOURCE_GS = 'G-21'
# DESTINATION_GS = 'G-24'
# RTT_CSV = 'kuiper_k1/ping_moscow_to_paris_rtt.csv'
# PATH_CHANGE_CSV = 'kuiper_k1/change_moscow_to_paris_path.csv'

# SOURCE_GS = 'G-0'
# DESTINATION_GS = 'G-84'
# RTT_CSV = 'kuiper_k1/ping_tokyo_to_sydney_rtt.csv'
# PATH_CHANGE_CSV = 'kuiper_k1/change_tokyo_to_sydney_path.csv'


# SOURCE_GS = 'G-1'
# DESTINATION_GS = 'G-9'
# RTT_CSV = 'starlink_s1/ping_delhi_to_new-york_rtt.csv'
# PATH_CHANGE_CSV = 'starlink_s1/change_delhi_to_new-york_path.csv'

# SOURCE_GS = 'G-21'
# DESTINATION_GS = 'G-24'
# RTT_CSV = 'starlink_s1/ping_moscow_to_paris_rtt.csv'
# PATH_CHANGE_CSV = 'starlink_s1/change_moscow_to_paris_path.csv'

# SOURCE_GS = 'G-0'
# DESTINATION_GS = 'G-84'
# RTT_CSV = 'starlink_s1/ping_tokyo_to_sydney_rtt.csv'
# PATH_CHANGE_CSV = 'starlink_s1/change_tokyo_to_sydney_path.csv'

# SOURCE_GS = 'G-1'
# DESTINATION_GS = 'G-9'
# RTT_CSV = 'telesat_t1/ping_delhi_to_new-york_rtt.csv'
# PATH_CHANGE_CSV = 'telesat_t1/change_delhi_to_new-york_path.csv'

# SOURCE_GS = 'G-21'
# DESTINATION_GS = 'G-24'
# RTT_CSV = 'telesat_t1/ping_moscow_to_paris_rtt.csv'
# PATH_CHANGE_CSV = 'telesat_t1/change_moscow_to_paris_path.csv'

SOURCE_GS = 'G-0'
DESTINATION_GS = 'G-84'
RTT_CSV = 'telesat_t1/ping_tokyo_to_sydney_rtt.csv'
PATH_CHANGE_CSV = 'telesat_t1/change_tokyo_to_sydney_path.csv'


__last_path = None
for second in range(200):

    # Build the constellation
    leo_con = LEOConstellation('LEOCON')
    leo_con.v.verbose = True
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
            # GroundStationAtCities.TOP_1000
        )
    )

    # # Kuiper
    # leo_con.add_shells(
    #     PlusGridShell(
    #         id=0,
    #         orbits=34,
    #         sat_per_orbit=34,
    #         altitude_m=630000.0,
    #         inclination_degree=51.9,

    #         angle_of_elevation_degree=35.0,
    #         phase_offset=50.0
    #     )
    # )

    # # Starlink
    # leo_con.add_shells(
    #     PlusGridShell(
    #         id=0,
    #         orbits=72,
    #         sat_per_orbit=22,
    #         altitude_m=550000.0,
    #         inclination_degree=53.0,

    #         angle_of_elevation_degree=25.0,
    #         phase_offset=50.0
    #     )
    # )

    # Telesat
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=27,
            sat_per_orbit=13,
            altitude_m=1015000.0,
            inclination_degree=98.98,

            angle_of_elevation_degree=10,
            phase_offset=50.0
        )
    )

    leo_con.set_time(second=second)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    # Generates all the routes
    # leo_con.generate_routes()

    # Generate shortest routes betweem source and destination ground stations
    try:
        leo_con.connect_ground_station(SOURCE_GS, DESTINATION_GS)
        compute_status, flow, k_path = k_shortest_paths(
            leo_con.sat_net_graph, SOURCE_GS, DESTINATION_GS, k=1
        )

        # Extract the shortest path
        # Calculate the path length
        # Compute the RTT in ms
        path = k_path[-1]
        route_length_m = 0

        for hop_id in range(len(path)-1):
            # print(path[hop_id], path[hop_id+1])
            route_length_m += leo_con.link_length(
                path[hop_id], path[hop_id+1]
            )

        #  Speed of light: 299792458 m/s
        RTT_ms = (1000*2*route_length_m)/299792458

    # When the either of the ground stations are not connected
    except networkx.exception.NodeNotFound:
        compute_status = 'False'
        path = list()
        RTT_ms = 0

    print()
    print(f"second: {second}")
    print(f"compute_status: {compute_status}")
    print(f"flow: {flow}")
    print(f"path: {path}")
    print(f"route_length_m: {route_length_m}")
    print(f"RTT_ms: {round(RTT_ms, 1)} ms")
    print()

    # Record the computed RTT.
    CSV_logger(
        {"time_s": second, "RTT_ms": RTT_ms},
        RTT_CSV
    )

    if __last_path is not None:
        # Record the path change time due to LEO dynamics
        if __last_path != path:
            CSV_logger(
                {"time_s": second},
                PATH_CHANGE_CSV
            )

    __last_path = path
