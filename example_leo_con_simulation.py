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


simulator = LEOConstellationSimulator(
    InternetTrafficAcrossCities.POP_GDP_100
)

for p in [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]:

    leo_con = LEOConstellation()
    leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
    leo_con.set_time()
    leo_con.set_loss_model(get_loss_model())

    # Starlink Shell 1
    leo_con.add_shells(
        PlusGridShell(
            id=0,
            orbits=72,
            sat_per_orbit=22,
            altitude_m=550000.0,
            inclination_degree=53.0,
            angle_of_elevation_degree=25.0,
            phase_offset=p
        )
    )
    leo_con.add_shells(
        PlusGridShell(
            id=1,
            orbits=72,
            sat_per_orbit=22,
            altitude_m=540000.0,
            inclination_degree=53.2,
            angle_of_elevation_degree=25.0,
            phase_offset=p
        )
    )
    leo_con.add_shells(
        PlusGridShell(
            id=2,
            orbits=36,
            sat_per_orbit=20,
            altitude_m=570000.0,
            inclination_degree=70.0,
            angle_of_elevation_degree=25.0,
            phase_offset=p
        )
    )

    simulator.add_constellation(leo_con)


simulator.simulate_in_serial()
# simulator.simulate_in_parallel()
