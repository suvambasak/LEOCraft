
'''
Generate a 3D view of the LEO constellation with inter-shell ISLs
Illustartes the how +Grid topology in inter-shell ISLs deforms over 
time due to orbital period difference of satellites in different shells 
altitudes. 

Figure is not included in the paper.
'''

import concurrent.futures
import multiprocessing as mp

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D


def build(t: int):
    leo_con = LEOConstellation(
        f'Inter Shell ISLs with {NUM_SHELLS} shells / Time: {t} second(s)'
    )
    leo_con.v.verbose = False
    leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))

    if NUM_SHELLS == 2:
        # Color code for shell 2
        COLORS = [RED, GREEN]
        _COLORS = [_RED, _GREEN]
    if NUM_SHELLS == 3:
        # Color code for shell 3
        COLORS = [RED, GREEN, BLUE, GREEN]
        _COLORS = [_RED, _GREEN, _BLUE, _GREEN]

    leo_con.add_shells(
        PlusGridZigzagElevation(


            altitude_pattern_m=[500000.0, 510000.0],
            # altitude_pattern_m=[500000.0, 510000.0, 520000.0, 510000.0,],


            id=0,
            orbits=20,
            sat_per_orbit=20,
            inclination_degree=80.0,
            angle_of_elevation_degree=30.0,
            phase_offset=0.0
        )
    )

    leo_con.set_time(second=t)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    sat_info = leo_con.sat_info('S0-0')
    view = SatRawView3D(
        leo_con,
        # lat=0.0,
        # long=-30.0,
        elevation_m=800000
    )
    view.v.verbose = False
    view._DEFAULT_SAT_SIZE = 20
    view._DEFAULT_WIDTH = 8
    view._shell_colors = []

    # Add color coded intra-orbit ISLs
    # ===============================================================================

    for o in range(8):

        view._ISL_COLOR = _COLORS[o % len(_COLORS)]

        # intra-orbit ISLs
        for sid in range(19):
            # print((f'S0-{sid+20*o}', f'S0-{(sid+1+20*o)}'))
            view.add_ISLs(((f'S0-{sid+20*o}', f'S0-{(sid+1+20*o)}'),))

        # print((f'S0-{sid+1+20*o}', f'S0-{(sid+1+20*o-19)}'))
        view.add_ISLs(((f'S0-{sid+1+20*o}', f'S0-{(sid+1+20*o-19)}'),))

        view.build()
        view._isl = set()

    view._ISL_COLOR = view._R_ISL_COLOR
    for s in range(19):
        view.add_ISLs((
            # (f'S0-{s}', f'S0-{s+1}'),
            # (f'S0-{s+20}', f'S0-{s+21}'),
            # (f'S0-{s+20*2}', f'S0-{s+20*2+1}'),
            # (f'S0-{s+20*3}', f'S0-{s+20*3+1}'),
            # (f'S0-{s+20*4}', f'S0-{s+20*4+1}'),
            # (f'S0-{s+20*5}', f'S0-{s+20*5+1}'),
            # (f'S0-{s+20*6}', f'S0-{s+20*6+1}'),
            # (f'S0-{s+20*7}', f'S0-{s+20*7+1}'),

            (f'S0-{s}', f'S0-{s+20}'),
            (f'S0-{s+20}', f'S0-{s+20*2}'),
            (f'S0-{s+20*2}', f'S0-{s+20*3}'),
            (f'S0-{s+20*3}', f'S0-{s+20*4}'),
            (f'S0-{s+20*4}', f'S0-{s+20*5}'),
            (f'S0-{s+20*5}', f'S0-{s+20*6}'),
            (f'S0-{s+20*6}', f'S0-{s+20*7}'),
        ))

    view.add_ISLs((
        # (f'S0-{19}', f'S0-{0}'),
        # (f'S0-{39}', f'S0-{20}'),
        # (f'S0-{59}', f'S0-{40}'),
        # (f'S0-{79}', f'S0-{60}'),
        # (f'S0-{99}', f'S0-{80}'),
        # (f'S0-{119}', f'S0-{100}'),
        # (f'S0-{120}', f'S0-{139}'),
        # (f'S0-{140}', f'S0-{159}'),

        (f'S0-{19}', f'S0-{39}'),
        (f'S0-{39}', f'S0-{59}'),
        (f'S0-{59}', f'S0-{79}'),
        (f'S0-{79}', f'S0-{99}'),
        (f'S0-{99}', f'S0-{119}'),
        (f'S0-{119}', f'S0-{139}'),
        (f'S0-{139}', f'S0-{159}'),
    ))

    # Satellites
    for o in range(8):
        view._shell_colors.append(COLORS[o % len(COLORS)])

        for sid in range(20*o, 20*(o+1)):
            view.add_satellites(f'S0-{sid}')

        view.build()
        view._sat = set()

    # view.show()

    view.export_png(f'{OUTPUT_DIR}/{str(t).zfill(10)}.png')
    print(f"|- {f'{OUTPUT_DIR}/{str(t).zfill(10)}.png'}")


if __name__ == '__main__':

    OUTPUT_DIR = 'shift'

    NUM_SHELLS = 3

    RED = 'rgb(153, 0, 0)'
    GREEN = 'rgb(0, 153, 0)'
    BLUE = 'rgb(0, 0, 153)'

    _RED = 'rgb(255, 0, 0)'
    _GREEN = 'rgb(0, 255, 0)'
    _BLUE = 'rgb(0, 0, 255)'

    with concurrent.futures.ProcessPoolExecutor(
            max_workers=3,
            mp_context=mp.get_context('fork')
    ) as executor:
        executor.map(build, range(0, 42*60*60, 10))
