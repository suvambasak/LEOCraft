

import concurrent.futures
from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.dataset import GroundStationAtCities
from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.user_terminals.ground_station import GroundStation
from LEOCraft.visuals.sat_view_2D import SatView2D


def leo_con_builder(inclination: int, time_s: int) -> LEOConstellation:

    leo_con = LEOConstellation()
    leo_con.v.verbose = False
    leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=20,
        sat_per_orbit=20,
        altitude_m=1000.0*600,
        inclination_degree=inclination,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    ))
    leo_con.set_time(second=time_s)
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    print('i=', inclination, 'time (m)=', time_s/60)

    return leo_con


if __name__ == '__main__':

    leo_con = LEOConstellation()
    leo_con.v.verbose = True
    leo_con.add_ground_stations(GroundStation(GroundStationAtCities.TOP_100))
    leo_con.add_shells(PlusGridShell(
        id=0,
        orbits=20,
        sat_per_orbit=20,
        altitude_m=1000.0*600,
        inclination_degree=50.0,
        angle_of_elevation_degree=25.0,
        phase_offset=50.0
    ))
    leo_con.set_time(minute=0)  # Time passed after epoch
    leo_con.set_loss_model(None)
    leo_con.build()
    leo_con.create_network_graph()

    # View
    view = SatView2D(leo_con)
    view.add_satellites('S0-0')
    view._shell_colors = ['rgb(255, 0, 0)',]
    view.build()
    view._sat = set()

    # ground track inclination 53 degree
    tasks = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for s in range(1, 60*120, 30):
            tasks.add(executor.submit(leo_con_builder, 50, s))

        for task in concurrent.futures.as_completed(tasks):
            view.leo_con = task.result()
            view.add_satellites('S0-0')
            view._shell_colors = ['rgb(255, 0, 0)',]
            view.build()
            view._sat = set()

    # ground track inclination 90 degree
    tasks = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for s in range(0, 60*120, 30):
            tasks.add(executor.submit(leo_con_builder, 80, s))

        for task in concurrent.futures.as_completed(tasks):
            view.leo_con = task.result()
            view.add_satellites('S0-0')
            view._shell_colors = ['rgb(0, 0, 255)',]
            view.build()
            view._sat = set()

view.show()
