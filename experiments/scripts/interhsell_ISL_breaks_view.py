import time

from LEOCraft.attenuation.fspl import FSPL
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities, InternetTrafficAcrossCities
from LEOCraft.performance.basic.coverage import Coverage
from LEOCraft.performance.basic.stretch import Stretch
from LEOCraft.performance.basic.throughput import Throughput
# from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.plus_grid_zigzag_elevation import PlusGridZigzagElevation
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_3D import SatView3D
from LEOCraft.visuals.sat_view_2D import SatView2D


start_time = time.perf_counter()

for t in range(0, 1500000, 1):
    print(f'>>>>>>>>>>>>>>>>> {t}')

    # # Pathloss model
    # loss_model = FSPL(
    #     28.5*1000000000,    # Frequency in Hz
    #     98.4,               # Tx power dBm
    #     0.5*1000000000,     # Bandwidth Hz
    #     13.6                # G/T ratio
    # )
    # loss_model.set_Tx_antenna_gain(gain_dB=34.5)

    leo_con = LEOConstellation('Starlink')
    leo_con.v.verbose = True
    leo_con.add_ground_stations(
        GroundStation(
            GroundStationAtCities.TOP_100
            # GroundStationAtCities.TOP_1000
            # GroundStationAtCities.COUNTRY_CAPITALS
        )
    )

    leo_con.add_shells(
        # PlusGridShell(
        #     id=0,
        #     orbits=10,
        #     sat_per_orbit=10,
        #     altitude_m=1500000.0,
        #     inclination_degree=60.0,
        #     angle_of_elevation_degree=30.0,
        #     phase_offset=0.0
        # )
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

    leo_con.set_time(hour=t)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    # leo_con.generate_routes()

    # # Throughput
    # th = Throughput(
    #     leo_con,
    #     InternetTrafficAcrossCities.ONLY_POP_100
    #     # InternetTrafficAcrossCities.POP_GDP_100
    #     # InternetTrafficAcrossCities.ONLY_POP_1000
    #     # InternetTrafficAcrossCities.COUNTRY_CAPITALS_ONLY_POP
    # )
    # th.build()
    # th.compute()

    # # Coverage
    # cov = Coverage(leo_con)
    # cov.build()
    # cov.compute()

    # # Latency/Stretch
    # sth = Stretch(leo_con)
    # sth.build()
    # sth.compute()

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
    view.export_png(
        f'/mnt/Storage/R-Projects/ResultsTrajectoryDesign/handoff/{str(t).zfill(10)}.png')

    # view = SatView2D(leo_con)

    # for i in range(50):
    #     view.add_satellites(f'S0-{i}')
    #     view.add_coverages(f'S0-{i}')
    # # view.add_all_ISLs()
    # # view.add_all_satellites()
    # # view.add_all_coverages()
    # view.build()
    # view.show()

    end_time = time.perf_counter()

    print(f'Total simulation time: {round((end_time-start_time)/60, 2)}m')
