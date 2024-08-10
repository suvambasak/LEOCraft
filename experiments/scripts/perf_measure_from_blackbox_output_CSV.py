import pandas as pd

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from LEOCraft.user_terminals.ground_station import GroundStation


INPUT_CSV_FILE = '/home/suvam/Projects/simulation-data-analysis/2025_INFOCOM/CSVs/optimization/DE/DE_DK.csv'
OUTPUT_CSV_FILE = 'DE_DK_PERF.csv'


df = pd.read_csv(INPUT_CSV_FILE)


def get_loss_model() -> FSPL:
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


simulator = LEOConstellationSimulator(
    InternetTrafficAcrossCities.ONLY_POP_100,
    # InternetTrafficAcrossCities.POP_GDP_100,
    OUTPUT_CSV_FILE
)


for row in df.itertuples(index=True, name='Pandas'):
    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(
        GroundStationAtCities.TOP_100
    ))
    leo_con.set_time()
    leo_con.set_loss_model(get_loss_model())

    leo_con.add_shells(
        PlusGridShell(
            id=0,

            orbits=row.o,
            sat_per_orbit=row.n,
            phase_offset=row.p,

            altitude_m=1000.0*row.h,
            angle_of_elevation_degree=row.e,
            inclination_degree=row.i
        )
    )

    simulator.add_constellation(leo_con)

perf_log = simulator.simulate_in_parallel(max_workers=4)
print(f'{OUTPUT_CSV_FILE}\tComplete.')
