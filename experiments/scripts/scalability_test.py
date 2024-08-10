import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.basic.stretch import Stretch
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation

start_time = time.perf_counter()


# Pathloss model
loss_model = FSPL(
    28.5*1000000000,    # Frequency in Hz
    98.4,               # Tx power dBm
    0.5*1000000000,     # Bandwidth Hz
    13.6                # G/T ratio
)
loss_model.set_Tx_antenna_gain(gain_dB=34.5)


leo_con = LEOConstellation('Starlink')
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        # GroundStationAtCities.TOP_100
        GroundStationAtCities.TOP_1000
        # GroundStationAtCities.COUNTRY_CAPITALS
    )
)


# # Shells original params(Gen 2)
# # Starlink Shell 1
# leo_con.add_shells(
#     PlusGridShell(
#         id=0,
#         orbits=28,
#         sat_per_orbit=120,
#         altitude_m=1000.0 * 525,
#         inclination_degree=53.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=1,
#         orbits=23,
#         sat_per_orbit=20,
#         altitude_m=1000.0 * 530,
#         inclination_degree=43.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 3
# leo_con.add_shells(
#     PlusGridShell(
#         id=2,
#         orbits=28,
#         sat_per_orbit=120,
#         altitude_m=1000.0 * 535,
#         inclination_degree=33.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 4
# leo_con.add_shells(
#     PlusGridShell(
#         id=3,
#         orbits=12,
#         sat_per_orbit=12,
#         altitude_m=1000.0 * 604,
#         inclination_degree=148.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 5
# leo_con.add_shells(
#     PlusGridShell(
#         id=4,
#         orbits=18,
#         sat_per_orbit=18,
#         altitude_m=1000.0 * 614,
#         inclination_degree=115.7,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 6
# leo_con.add_shells(
#     PlusGridShell(
#         id=5,
#         orbits=30,
#         sat_per_orbit=120,
#         altitude_m=1000.0 * 360,
#         inclination_degree=96.9,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 7
# leo_con.add_shells(
#     PlusGridShell(
#         id=6,
#         orbits=48,
#         sat_per_orbit=110,
#         altitude_m=1000.0 * 350,
#         inclination_degree=38.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 8
# leo_con.add_shells(
#     PlusGridShell(
#         id=7,
#         orbits=48,
#         sat_per_orbit=110,
#         altitude_m=1000.0 * 345,
#         inclination_degree=46.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink Shell 9
# leo_con.add_shells(
#     PlusGridShell(
#         id=8,
#         orbits=48,
#         sat_per_orbit=110,
#         altitude_m=1000.0 * 340,
#         inclination_degree=53.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink (Gen 1) Shell 1
# leo_con.add_shells(
#     PlusGridShell(
#         id=9,
#         orbits=72,
#         sat_per_orbit=22,
#         altitude_m=550000.0,
#         inclination_degree=53.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink (Gen 1) Shell 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=10,
#         orbits=72,
#         sat_per_orbit=22,
#         altitude_m=540000.0,
#         inclination_degree=53.2,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Starlink (Gen 1) Shell 3
# leo_con.add_shells(
#     PlusGridShell(
#         id=11,
#         orbits=36,
#         sat_per_orbit=20,
#         altitude_m=570000.0,
#         inclination_degree=70.0,
#         angle_of_elevation_degree=25.0,
#         phase_offset=50.0
#     )
# )

# # Kuiper Shell 1
# leo_con.add_shells(
#     PlusGridShell(
#         id=12,
#         orbits=34,
#         sat_per_orbit=34,
#         altitude_m=1000.0 * 630,
#         inclination_degree=51.9,
#         angle_of_elevation_degree=35.0,
#         phase_offset=50.0
#     )
# )

# # Kuiper Shell 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=13,
#         orbits=36,
#         sat_per_orbit=36,
#         altitude_m=1000.0 * 610,
#         inclination_degree=42.0,
#         angle_of_elevation_degree=35.0,
#         phase_offset=50.0
#     )
# )

# # Kuiper Shell 3
# leo_con.add_shells(
#     PlusGridShell(
#         id=14,
#         orbits=28,
#         sat_per_orbit=28,
#         altitude_m=1000.0 * 590,
#         inclination_degree=33.0,
#         angle_of_elevation_degree=35.0,
#         phase_offset=50.0
#     )
# )

# # OneWeb 1
# leo_con.add_shells(
#     PlusGridShell(
#         id=15,
#         orbits=36,
#         sat_per_orbit=49,
#         altitude_m=1000.0 * 1200,
#         inclination_degree=87.9,
#         angle_of_elevation_degree=5.0,
#         phase_offset=50.0
#     )
# )

# # OneWeb 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=16,
#         orbits=32,
#         sat_per_orbit=720,
#         altitude_m=1000.0 * 1200,
#         inclination_degree=40.0,
#         angle_of_elevation_degree=5.0,
#         phase_offset=50.0
#     )
# )

# # OneWeb 3
# leo_con.add_shells(
#     PlusGridShell(
#         id=17,
#         orbits=32,
#         sat_per_orbit=720,
#         altitude_m=1000.0 * 1200,
#         inclination_degree=55.0,
#         angle_of_elevation_degree=5.0,
#         phase_offset=50.0
#     )
# )

# # Telesat 1
# leo_con.add_shells(
#     PlusGridShell(
#         id=18,
#         orbits=27,
#         sat_per_orbit=13,
#         altitude_m=1000.0 * 1015,
#         inclination_degree=98.98,
#         angle_of_elevation_degree=10.0,
#         phase_offset=50.0
#     )
# )

# # Telesat 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=19,
#         orbits=40,
#         sat_per_orbit=33,
#         altitude_m=1000.0 * 1325,
#         inclination_degree=50.88,
#         angle_of_elevation_degree=10.0,
#         phase_offset=50.0
#     )
# )


# # Telesat 2
# leo_con.add_shells(
#     PlusGridShell(
#         id=19,
#         orbits=40,
#         sat_per_orbit=33,
#         altitude_m=1000.0 * 1325,
#         inclination_degree=50.88,
#         angle_of_elevation_degree=10.0,
#         phase_offset=50.0
#     )
# )


# # All in single shell - total: 83727
# leo_con.add_shells(
#     PlusGridShell(
#         id=0,
#         orbits=443,
#         sat_per_orbit=189,
#         altitude_m=1000.0 * 550,
#         inclination_degree=90,
#         angle_of_elevation_degree=20.0,
#         phase_offset=50.0
#     )
# )


# All in single shell - total: 83727 (feasibility test)
leo_con.add_shells(
    PlusGridShell(
        id=0,
        orbits=3987,
        sat_per_orbit=21,
        altitude_m=1000.0 * 550,
        inclination_degree=40,
        angle_of_elevation_degree=10.0,
        phase_offset=50.0
    )
)

leo_con.set_time()  # Time passed after epoch
leo_con.set_loss_model(loss_model)
leo_con.build()
leo_con.create_network_graph()

leo_con.generate_routes()


# Throughput
th = Throughput(
    leo_con,
    # InternetTrafficAcrossCities.ONLY_POP_100
    # InternetTrafficAcrossCities.POP_GDP_100
    InternetTrafficAcrossCities.ONLY_POP_1000
    # InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
)
th.build()
th.compute()


# Coverage
cov = Coverage(leo_con)
cov.build()
cov.compute()


# Latency/Stretch
sth = Stretch(leo_con)
sth.build()
sth.compute()


end_time = time.perf_counter()


# # Exporting all simulation datasets
# ouput_path = '/home/suvam/Desktop/Starlink'

# # Constellation
# leo_con.export_gsls(ouput_path)
# leo_con.export_routes(ouput_path)
# leo_con.export_no_path_found(ouput_path)
# leo_con.export_k_path_not_found(ouput_path)

# # Shells
# for shell in leo_con.shells:
#     shell.export_satellites(ouput_path)
#     shell.export_isls(ouput_path)

# # Ground stations
# leo_con.ground_stations.export(ouput_path)

# # Throughputs
# th.export_path_selection(ouput_path)
# th.export_LP_model(ouput_path)

# # Stretch
# sth.export_stretch_dataset(ouput_path)


print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
