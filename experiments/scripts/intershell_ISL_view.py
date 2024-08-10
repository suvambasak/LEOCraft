from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D

leo_con = LEOConstellation('MultiShell-ISLs')
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        GroundStationAtCities.TOP_100
        # GroundStationAtCities.TOP_1000
        # GroundStationAtCities.COUNTRY_CAPITALS
    )
)


# print('SINGLE SHELL')
# leo_con.add_shells(PlusGridShell(
#     id=0,
#     orbits=15,
#     sat_per_orbit=15,
#     altitude_m=550000.0,
#     inclination_degree=50.0,
#     angle_of_elevation_degree=30.0,
#     phase_offset=50.0
# ))

# print('MULT SHELL')
# leo_con.add_shells(PlusGridZigzagElevation(
#     id=0,
#     orbits=323,
#     sat_per_orbit=10,
#     altitude_pattern_m=[590000.0, 610000.0, 630000.0, 610000.0],
#     inclination_degree=51.9,
#     angle_of_elevation_degree=35.0,
#     phase_offset=50.0
# ))


print('MULT SHELL - experiments')
leo_con.add_shells(PlusGridZigzagElevation(
    id=0,
    orbits=20,
    sat_per_orbit=20,
    altitude_pattern_m=[500000.0, 1000000.0],
    # altitude_pattern_m=[500000.0, 1000000.0, 1500000.0, 1000000.0,],
    inclination_degree=80.0,
    angle_of_elevation_degree=30.0,
    phase_offset=0.0
))


# leo_con.add_shells(
#     PlusGridShell(
#         id=0,

#         orbits=20,
#         sat_per_orbit=20,

#         altitude_m=500*1000.0,

#         inclination_degree=50.0,
#         angle_of_elevation_degree=10.8,

#         phase_offset=0.0
#     )
# )

# leo_con.add_shells(
#     PlusGridZigzagElevation(
#         id=1,

#         orbits=20,
#         sat_per_orbit=20,

#         altitude_pattern_m=[1000*1000.0, 1500*1000.0],

#         inclination_degree=80.0,
#         angle_of_elevation_degree=30.0,

#         phase_offset=0.0
#     )
# )


leo_con.set_time(minute=0)  # Time passed after epoch
leo_con.set_loss_model(None)
leo_con.build()
leo_con.create_network_graph()


# leo_con.generate_routes()
sat_info = leo_con.sat_info('S0-0')
view = SatRawView3D(
    leo_con,
    # globe_visibility=False,
    lat=sat_info.nadir_latitude_deg,
    long=sat_info.nadir_longitude_deg,
    elevation_m=800000,
    # globe_radius_km=500
)


# view.add_all_satellites()
# view.add_all_ISLs()


for s in range(20*8):
    view.add_satellites(f'S0-{s}')

for s in range(19):
    view.add_ISLs((
        (f'S0-{s}', f'S0-{s+1}'),
        (f'S0-{s+20}', f'S0-{s+21}'),
        (f'S0-{s+20*2}', f'S0-{s+20*2+1}'),
        (f'S0-{s+20*3}', f'S0-{s+20*3+1}'),
        (f'S0-{s+20*4}', f'S0-{s+20*4+1}'),
        (f'S0-{s+20*5}', f'S0-{s+20*5+1}'),
        (f'S0-{s+20*6}', f'S0-{s+20*6+1}'),
        (f'S0-{s+20*7}', f'S0-{s+20*7+1}'),

        (f'S0-{s}', f'S0-{s+20}'),
        (f'S0-{s+20}', f'S0-{s+20*2}'),
        (f'S0-{s+20*2}', f'S0-{s+20*3}'),
        (f'S0-{s+20*3}', f'S0-{s+20*4}'),
        (f'S0-{s+20*4}', f'S0-{s+20*5}'),
        (f'S0-{s+20*5}', f'S0-{s+20*6}'),
        (f'S0-{s+20*6}', f'S0-{s+20*7}'),
    ))

view.add_ISLs((
    (f'S0-{19}', f'S0-{0}'),
    (f'S0-{39}', f'S0-{20}'),
    (f'S0-{59}', f'S0-{40}'),
    (f'S0-{79}', f'S0-{60}'),
    (f'S0-{99}', f'S0-{80}'),
    (f'S0-{119}', f'S0-{100}'),
    (f'S0-{120}', f'S0-{139}'),
    (f'S0-{140}', f'S0-{159}'),

    (f'S0-{19}', f'S0-{39}'),
    (f'S0-{39}', f'S0-{59}'),
    (f'S0-{59}', f'S0-{79}'),
    (f'S0-{79}', f'S0-{99}'),
    (f'S0-{99}', f'S0-{119}'),
    (f'S0-{119}', f'S0-{139}'),
    (f'S0-{139}', f'S0-{159}'),
))


# for s in range(20*8):
#     view.add_satellites(f'S1-{s}')

# for s in range(19):
#     view.add_ISLs((
#         (f'S1-{s}', f'S1-{s+1}'),
#         (f'S1-{s+20}', f'S1-{s+21}'),
#         (f'S1-{s+20*2}', f'S1-{s+20*2+1}'),
#         (f'S1-{s+20*3}', f'S1-{s+20*3+1}'),
#         (f'S1-{s+20*4}', f'S1-{s+20*4+1}'),
#         (f'S1-{s+20*5}', f'S1-{s+20*5+1}'),
#         (f'S1-{s+20*6}', f'S1-{s+20*6+1}'),
#         (f'S1-{s+20*7}', f'S1-{s+20*7+1}'),

#         (f'S1-{s}', f'S1-{s+20}'),
#         (f'S1-{s+20}', f'S1-{s+20*2}'),
#         (f'S1-{s+20*2}', f'S1-{s+20*3}'),
#         (f'S1-{s+20*3}', f'S1-{s+20*4}'),
#         (f'S1-{s+20*4}', f'S1-{s+20*5}'),
#         (f'S1-{s+20*5}', f'S1-{s+20*6}'),
#         (f'S1-{s+20*6}', f'S1-{s+20*7}'),
#     ))

# view.add_ISLs((
#     (f'S1-{19}', f'S1-{0}'),
#     (f'S1-{39}', f'S1-{20}'),
#     (f'S1-{59}', f'S1-{40}'),
#     (f'S1-{79}', f'S1-{60}'),
#     (f'S1-{99}', f'S1-{80}'),
#     (f'S1-{119}', f'S1-{100}'),
#     (f'S1-{120}', f'S1-{139}'),
#     (f'S1-{140}', f'S1-{159}'),

#     (f'S1-{19}', f'S1-{39}'),
#     (f'S1-{39}', f'S1-{59}'),
#     (f'S1-{59}', f'S1-{79}'),
#     (f'S1-{79}', f'S1-{99}'),
#     (f'S1-{99}', f'S1-{119}'),
#     (f'S1-{119}', f'S1-{139}'),
#     (f'S1-{139}', f'S1-{159}'),
# ))

view.build()
view.show()
# view.export_png()
# view.export_html('/home/suvam/Desktop/UPDATE/MultiShell-3.html')
