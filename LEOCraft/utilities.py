import sys
from itertools import islice

import networkx as nx


def k_shortest_paths(sat_net_graph: nx.Graph, source: str, target: str, k: int, weight: str = "weight") -> tuple[bool, str, list[list[str]]]:
    """Find K shortest path in given networkx graph

    Parameters:
    -------
    sat_net_graph: nx.Graph
        Network Graph
    source: str
        Source node
    target: str
        Destination node
    k: int
        Number of sortest routes
    weight: str, optional
        Weight parameter (distance)

    Returns
    -------
    tuple[bool, str, list[list[str]]]
        Status, flow, list of k shortest path
    """
    flow = f"{source}_{target}"
    try:
        return True, flow, list(
            islice(nx.shortest_simple_paths(
                sat_net_graph, source, target, weight=weight), k
            )
        )
    except nx.NetworkXNoPath as e:
        # If no path found return status False and empty list
        print(f'Exeption[{flow}]: {str(e)}')
        return False, flow, []


class ProcessingLog:
    "Show processing logs in console"

    verbose = True

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def rlog(self, msg: str) -> None:
        if self.verbose:
            sys.stdout.write(f'\r {msg}')

    def clr(self) -> None:
        if self.verbose:
            sys.stdout.write(
                '\r                                                                        \r'
            )
