import sys

LEOCRAFT_PATH = '/home/suvam/Projects/LEOCraft'
sys.path.append(LEOCRAFT_PATH)


def get_possible_oxn_arrangements(total_sat: int, min_sat_per_orbit: int) -> list[tuple[int, int]]:
    '''Generate all possible orbits x satellites/orbit arrangments in the given budget

    Parameters
    ----------
    total_sat: int
        Total number of satellites in the constellation (single shell)

    min_sat_per_orbit: int
        Minimum number of satellites in each orbit

    Returns
    -------
    list[tuple[int, int]]
        All possible arrangments
    '''

    oxn: list[tuple[int, int]] = []

    for orbital_plane in range(min_sat_per_orbit, total_sat):
        if total_sat % orbital_plane == 0 and total_sat/orbital_plane >= min_sat_per_orbit:
            oxn.append((orbital_plane, int(total_sat/orbital_plane)))

    assert len(oxn) > 0
    return oxn


class PerformanceCache:
    def __init__(self) -> None:
        self._cache = dict()

    def add(self, key: str, performance: float) -> None:
        self._cache[key] = performance

    def get(self, key: str) -> float:
        return self._cache.get(key)
