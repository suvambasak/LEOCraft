from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell


# Test Shell
PlusGridShell(
    id=0,
    orbits=25,
    sat_per_orbit=25,
    altitude_m=550000.0,
    inclination_degree=90.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)


# Starlink Shell 5 (Gen2)
PlusGridShell(
    id=0,
    orbits=28,
    sat_per_orbit=120,
    altitude_m=525000.0,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)


# HP Starlink Shell 1
PlusGridShell(
    id=0,
    orbits=144,
    sat_per_orbit=11,
    altitude_m=550000.0,
    inclination_degree=35.0,
    angle_of_elevation_degree=15.0,
    phase_offset=50.0
)

# Starlink Shell 1
PlusGridShell(
    id=0,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=550000.0,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)

PlusGridShell(
    id=1,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=540000.0,
    inclination_degree=53.2,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)

PlusGridShell(
    id=2,
    orbits=36,
    sat_per_orbit=20,
    altitude_m=570000.0,
    inclination_degree=70.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
