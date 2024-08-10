import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import \
    PlusGridZigzagElevation
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from LEOCraft.user_terminals.ground_station import GroundStation

start_time = time.perf_counter()


def get_loss_model() -> FSPL:
    loss_model = FSPL(
        28.5*1000000000,    # Frequency in Hz
        98.4,               # Tx power dBm
        0.5*1000000000,     # Bandwidth Hz
        13.6                # G/T ratio
    )
    loss_model.set_Tx_antenna_gain(gain_dB=34.5)
    return loss_model


if __name__ == '__main__':

    # Parameters
    CSV_FILE = '500.csv'
    TOTAL_SAT = 500
    MIN_SAT_PER_ORBIT = 10

    h = 1000
    e = 16.4
    i = 33.0

    oxn = []
    for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
        if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
            oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

    # Simulation setup
    simulator = LEOConstellationSimulator(
        InternetTrafficAcrossCities.ONLY_POP_100,
        # InternetTrafficAcrossCities.POP_GDP_100,
        CSV_FILE
    )

    for o, n in oxn:
        for p in range(0, 51, 10):

            leo_con = LEOConstellation()
            leo_con.add_ground_stations(GroundStation(
                GroundStationAtCities.TOP_100
            ))
            leo_con.set_time()
            leo_con.set_loss_model(get_loss_model())

            leo_con.add_shells(
                PlusGridShell(
                    id=0,

                    orbits=o,
                    sat_per_orbit=n,
                    phase_offset=p,

                    altitude_m=1000.0*h,
                    angle_of_elevation_degree=e,
                    inclination_degree=i
                )
            )

            simulator.add_constellation(leo_con)

    # simulator.simulate_in_serial()
    perf_log = simulator.simulate_in_parallel(max_workers=3)
    print(f'{CSV_FILE}\tComplete.')


end_time = time.perf_counter()
print('\n\n TOTAL TIME TAKEN: ', end_time-start_time)
