
'''
This script illustrates how intershell ISLs goes out of range 
by rendering frame by frame 3D view of inter and intra shell 
ISLs between two consecutive orbits in .
'''


import time

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D

OUTPUT_DIR = 'intershell_ISL_breaks_view'


start_time = time.perf_counter()

for t in range(0, 1500000):
    print('___________________________', 'Time:', t)

    leo_con = LEOConstellation('Starlink')
    leo_con.v.verbose = True
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
        )
    )

    leo_con.add_shells(
        PlusGridZigzagElevation(
            id=0,
            orbits=72,
            sat_per_orbit=22,
            altitude_pattern_m=[550000.0, 560000.0],
            inclination_degree=53.0,
            angle_of_elevation_degree=25.0,
            phase_offset=0.0
        )
    )

    leo_con.set_time(minute=t)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    sat_info = leo_con.sat_info("S0-0")
    view = SatView3D(
        leo_con,
        lat=sat_info.nadir_latitude_deg,
        long=sat_info.nadir_longitude_deg,
        title=f'Time: {t}h'
    )
    # view.add_all_satellites()
    # view.add_all_ISLs()

    for s in range(22*2):
        view.add_satellites(f'S0-{s}')

    l = []
    for s in range(21):
        l.append((f'S0-{s}', f'S0-{s+1}'))
        l.append((f'S0-{s+22}', f'S0-{s+22+1}'))
        l.append((f'S0-{s}', f'S0-{s+22}'))

    l.append((f'S0-21', f'S0-0'))
    l.append((f'S0-43', f'S0-22'))
    l.append((f'S0-21', f'S0-43'))

    view.add_ISLs(l)

    view.highlight_satellites(['S0-22'])

    view.build()
    # view.show()
    view.export_png(f'{OUTPUT_DIR}/{str(t).zfill(10)}.png')


end_time = time.perf_counter()

print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
