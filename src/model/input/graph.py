from copy import deepcopy


def _sym(routes: list[tuple[int, int, int, int]]):
    original = deepcopy(routes)
    symmetrical = [(b, a, dist, time) for a, b, dist, time in original]

    nodes = {t[0] for t in original} | {t[1] for t in original}

    return original + symmetrical + [(a, a, 0, 0) for a in nodes]


class Graph:
    """
    routes : list[(a, b, dist, time minutes)]
    """

    def __init__(self, routes: list[tuple[int, int, int, int]], warehouse=0):
        """
        routes : list[(a, b, dist, time minutes)]
        """
        self.routes = _sym(routes)
        self.warehouse = warehouse

        self.n_nodes = len(set([t[0] for t in self.routes]))
