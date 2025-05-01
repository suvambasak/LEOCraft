'''
This file contains design paramaters proposed by different LEO satellite constellation operator.
Sources:
- https://fcc.report/IBFS/SAT-MOD-20200417-00037/2274315.pdf
- https://fcc.report/IBFS/SAT-MPL-20200526-00053/2378318.pdf
- https://fcc.report/IBFS/SAT-MPL-20200526-00062/2379706.pdf
- https://www.fcc.gov/document/fcc-partially-grants-spacex-gen2-broadband-satellite-application
- https://fcc.report/IBFS/SAT-LOA-20190704-00057/1773885.pdf
- https://fcc.report/IBFS/SAT-MPL-20200526-00053/2378320.pdf
'''


from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell


# Simple sample params to test the LEOCraft
PlusGridShell(
    id=0,
    orbits=25,
    sat_per_orbit=25,
    altitude_m=550000.0,
    inclination_degree=90.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)


# Starlink LEO constellations


# Gen 1
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
# Starlink Shell 3
PlusGridShell(
    id=1,
    orbits=72,
    sat_per_orbit=22,
    altitude_m=540000.0,
    inclination_degree=53.2,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 3
PlusGridShell(
    id=2,
    orbits=36,
    sat_per_orbit=20,
    altitude_m=570000.0,
    inclination_degree=70.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)


# Optimized Starlink Shell 1 using out traffic matrics and gound station locations
PlusGridShell(
    id=0,
    orbits=144,
    sat_per_orbit=11,
    altitude_m=550000.0,
    inclination_degree=35.0,
    angle_of_elevation_degree=15.0,
    phase_offset=50.0
)

# Starlink Gen 2

# Starlink Shell 1 (Gen2)
PlusGridShell(
    id=0,
    orbits=48,
    sat_per_orbit=110,
    altitude_m=340000.0,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 2 (Gen2)
PlusGridShell(
    id=2,
    orbits=48,
    sat_per_orbit=110,
    altitude_m=345000.0,
    inclination_degree=46.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 3 (Gen2)
PlusGridShell(
    id=3,
    orbits=48,
    sat_per_orbit=110,
    altitude_m=350000.0,
    inclination_degree=38.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 4 (Gen2)
PlusGridShell(
    id=3,
    orbits=30,
    sat_per_orbit=120,
    altitude_m=360000.0,
    inclination_degree=96.9,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 5 (Gen2)
PlusGridShell(
    id=5,
    orbits=28,
    sat_per_orbit=120,
    altitude_m=525000.0,
    inclination_degree=53.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 6 (Gen2)
PlusGridShell(
    id=6,
    orbits=23,
    sat_per_orbit=20,
    altitude_m=530000.0,
    inclination_degree=43.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 7 (Gen2)
PlusGridShell(
    id=7,
    orbits=28,
    sat_per_orbit=120,
    altitude_m=535000.0,
    inclination_degree=33.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 8 (Gen2)
PlusGridShell(
    id=8,
    orbits=12,
    sat_per_orbit=12,
    altitude_m=604000.0,
    inclination_degree=148.0,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)
# Starlink Shell 9 (Gen2)
PlusGridShell(
    id=9,
    orbits=18,
    sat_per_orbit=18,
    altitude_m=614000.0,
    inclination_degree=115.7,
    angle_of_elevation_degree=25.0,
    phase_offset=50.0
)


# Amazon Project Kuiper systems

# Kuiper Shell 1
PlusGridShell(
    id=0,
    orbits=34,
    sat_per_orbit=34,
    altitude_m=630000.0,
    inclination_degree=51.9,
    angle_of_elevation_degree=35.0,
    phase_offset=50.0
)
# Kuiper Shell 2
PlusGridShell(
    id=1,
    orbits=36,
    sat_per_orbit=36,
    altitude_m=610000.0,
    inclination_degree=42.0,
    angle_of_elevation_degree=35.0,
    phase_offset=50.0
)
# Kuiper Shell 3
PlusGridShell(
    id=2,
    orbits=28,
    sat_per_orbit=28,
    altitude_m=590000.0,
    inclination_degree=33.0,
    angle_of_elevation_degree=35.0,
    phase_offset=50.0
)


# OneWeb
# OneWeb Shell 1
PlusGridShell(
    id=0,
    orbits=36,
    sat_per_orbit=49,
    altitude_m=1200000.0,
    inclination_degree=87.9,
    angle_of_elevation_degree=5.0,
    phase_offset=50.0
)
# OneWeb Shell 2
PlusGridShell(
    id=1,
    orbits=32,
    sat_per_orbit=720,
    altitude_m=1200000.0,
    inclination_degree=40.0,
    angle_of_elevation_degree=5.0,
    phase_offset=50.0
)
# OneWeb Shell 3
PlusGridShell(
    id=2,
    orbits=32,
    sat_per_orbit=720,
    altitude_m=1200000.0,
    inclination_degree=55.0,
    angle_of_elevation_degree=5.0,
    phase_offset=50.0
)
