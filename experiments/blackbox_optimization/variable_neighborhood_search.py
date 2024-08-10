import time

from experiments.blackbox_optimization.common import *
from LEOCraft.optimization.best_first_search import BestFirstSearch
from LEOCraft.utilities import CSV_logger

if __name__ == '__main__':
    TOTAL_SATS = 720
    MIN_SAT_PER_ORBIT = 10
    ALTITUDE_UB_KM = 575
    ALTITUDE_LB_KM = 565

    OXN = get_possible_oxn_arrangements(TOTAL_SATS, MIN_SAT_PER_ORBIT)
    CSV = 'VNS_DK.csv'

    _start_time = time.perf_counter()
    bfs = BestFirstSearch(
        e=10.0,
        h=(ALTITUDE_UB_KM+ALTITUDE_LB_KM)/2,
        i=30.0,

        n=OXN[-1][1],
        o=OXN[-1][0],
        p=50
    )
    bfs.set_h_bound(ALTITUDE_UB_KM, ALTITUDE_LB_KM)
    bfs.set_max_step_size(hstep=5, istep=5, estep=5)
    result = bfs.search(tolerance=3, max_iter=100)

    _end_time = time.perf_counter()
    print(f"""Total optimization time: {
        round((_end_time-_start_time)/3600, 2)}h""")
    result['time_s'] = _end_time-_start_time
    result['total_sat'] = TOTAL_SATS
    CSV_logger(result, CSV)
