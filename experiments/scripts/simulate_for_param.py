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
    CSV_FILE = '30x30_optimized.csv'
    # TOTAL_SAT = 324*12
    # MIN_SAT_PER_ORBIT = 10

    # # Starlink Shell-1
    # h = 550
    # e = 25
    # i = 53

    # o = 72
    # n = 22
    # p = 50

    t_m = 0

    # oxn = []
    # for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
    #     if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
    #         oxn.append((orbital_plane, int(TOTAL_SAT/orbital_plane)))

    # Simulation setup
    simulator = LEOConstellationSimulator(
        InternetTrafficAcrossCities.ONLY_POP_100,
        # InternetTrafficAcrossCities.POP_GDP_100,
        CSV_FILE
    )

    for t_m in range(0, 24*60+1, 5):
        # for h in range(500, 1001, 10):
        # for e in range(5, 50+1, 3):
        # for i in range(5, 90+1, 3):
        # for p in range(0, 51, 5):
        # for o, n in oxn:

        # print(t_m)
        # continue

        leo_con = LEOConstellation()
        leo_con.add_ground_stations(GroundStation(
            GroundStationAtCities.TOP_100
        ))
        leo_con.set_time(minute=t_m)
        leo_con.set_loss_model(get_loss_model())

        leo_con.add_shells(
            # PlusGridShell(
            #     id=0,

            #     orbits=o,
            #     sat_per_orbit=n,
            #     phase_offset=p,

            #     altitude_m=1000.0*h,
            #     angle_of_elevation_degree=e,
            #     inclination_degree=i
            # )

            # Shell - 3
            # PlusGridZigzagElevation(
            #     id=0,
            #     orbits=324,
            #     sat_per_orbit=12,
            #     altitude_pattern_m=[540000.0, 550000.0, 570000.0, 550000.0],
            #     inclination_degree=44.3,
            #     angle_of_elevation_degree=16.6,
            #     phase_offset=50.0
            # )


            # # Shell - 2
            # PlusGridZigzagElevation(
            #     id=0,
            #     orbits=324,
            #     sat_per_orbit=12,
            #     altitude_pattern_m=[540000.0, 550000.0],
            #     inclination_degree=46.1,
            #     angle_of_elevation_degree=16.2,
            #     phase_offset=50.0
            # )

            # Shell - 1
            # PlusGridShell(
            #     id=0,
            #     orbits=324,
            #     sat_per_orbit=12,
            #     altitude_m=550000.0,
            #     inclination_degree=45.3,
            #     angle_of_elevation_degree=16.4,
            #     phase_offset=50.0
            # )

            # Test fluctuation with size
            PlusGridShell(
                id=0,
                orbits=90,
                sat_per_orbit=10,
                altitude_m=550000.0,
                inclination_degree=35.1,
                angle_of_elevation_degree=10.5,
                phase_offset=50.0
            )

        )

        simulator.add_constellation(leo_con)

    # simulator.simulate_in_serial()
    perf_log = simulator.simulate_in_parallel(max_workers=4)

    # print('-----------------------')
    # print(perf_log)
    # print('-----------------------')
    # print(len(perf_log))

    print(f'{CSV_FILE}\tComplete.')

    end_time = time.perf_counter()
    print('\n\n TOTAL TIME TAKEN: ', end_time-start_time)
