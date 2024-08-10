
from LEOCraft.optimization.best_first_search import BestFirstSearch

bfs = BestFirstSearch(
    e=10.0,
    h=550,
    i=30.0,
    p=50,

    o=90,
    n=10
)


# bfs.set_e_bound(20, 30)
# bfs.set_h_bound(560, 580)
# bfs.set_i_bound(30, 90)
bfs.set_max_step_size(hstep=0, istep=5, estep=5)

bfs.search(tolerance=3, max_iter=100)
