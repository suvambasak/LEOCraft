from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.simulator.LEO_constellation_simulator import \
    LEOConstellationSimulator
from LEOCraft.user_terminals.ground_station import GroundStation


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
    # CSV_FILE = 'e_5_50.csv'
    # CSV_FILE = 'h_24.csv'
    # CSV_FILE = 'h_300_2000.csv'
    # CSV_FILE = 'i_5_175.csv'
    # CSV_FILE = 'oxn.csv'
    # CSV_FILE = 'p_0_50.csv'

    # CSV_FILE = 'HP_oxn.csv'
    CSV_FILE = 'HP_p_0_50.csv'

    TOTAL_SAT = 72*22
    MIN_SAT_PER_ORBIT = 10

    # Starlink Shell-1
    h = 550
    # e = 25
    # i = 53
    i = 40
    e = 15

    o = 72
    n = 22
    p = 50

    t_m = 0

    oxn = []
    for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
        if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
            oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

    # Simulation setup
    simulator = LEOConstellationSimulator(
        # InternetTrafficAcrossCities.POP_GDP_100,
        # InternetTrafficAcrossCities.ONLY_POP_100,
        InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP,
        CSV_FILE
    )

    # for t_m in range(0, 24*60+1, 5):
    # for h in range(300, 2001, 10):
    # for e in range(5, 51, 2):
    # for i in range(5, 176, 3):
    for p in range(0, 51, 5):
        # for o, n in oxn:

        leo_con = LEOConstellation()
        leo_con.add_ground_stations(GroundStation(
            # GroundStationAtCities.TOP_100
            GroundStationAtCities.COUNTRY_CAPITALS
        ))
        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())

        # Starlink Shell 1
        leo_con.add_shells(PlusGridShell(
            id=0,

            orbits=o,
            sat_per_orbit=n,
            phase_offset=p,

            altitude_m=1000.0*h,
            angle_of_elevation_degree=e,
            inclination_degree=i
        ))

        simulator.add_constellation(leo_con)

    # simulator.simulate_in_serial()
    simulator.simulate_in_parallel(max_workers=3)

    print(f'{CSV_FILE}\tComplete.')
