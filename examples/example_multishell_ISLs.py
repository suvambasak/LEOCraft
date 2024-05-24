import time

from project_path import *

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.basic.stretch import Stretch
from LEOCraft.performance.basic.throughput import Throughput
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
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


leo_con = LEOConstellation('MultiShell')
leo_con.v.verbose = True
leo_con.add_ground_stations(
    GroundStation(
        # GroundStationAtCities.TOP_100
        # GroundStationAtCities.TOP_1000
        GroundStationAtCities.COUNTRY_CAPITALS
    )
)

# Adding Shells
# Starlink Shell 1
leo_con.add_shells(
    PlusGridZigzagElevation(
        id=0,
        orbits=20,
        sat_per_orbit=20,
        # altitude_pattern_m=[500000.0, 1000000.0],
        altitude_pattern_m=[500000.0, 1000000.0, 1500000.0, 1000000.0,],
        inclination_degree=80.0,
        angle_of_elevation_degree=30.0,
        phase_offset=0.0
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
    # InternetTrafficAcrossCities.ONLY_POP_1000
    InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
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
print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
