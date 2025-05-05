from copy import deepcopy
import pandas as pd
import numpy as np


def _sym(routes: list[tuple[int, int, float, float]]):
    original = deepcopy(routes)
    symmetrical = [(b, a, dist, time) for a, b, dist, time in original]

    nodes = {t[0] for t in original} | {t[1] for t in original}

    return original + symmetrical + [(a, a, 0, 0) for a in nodes]


class Graph:
    """
    routes : list[(a, b, dist, time minutes)]
    """

    def __init__(
        self,
        routes: list[tuple[int, int, float, float]],
        points: np.ndarray,
        warehouse=0,
    ):
        """
        routes : list[(a, b, dist, time minutes)]
        """
        self.routes = _sym(routes)
        self.warehouse = warehouse

        self.n_nodes = len(set([t[0] for t in self.routes]))

        self.points = points

    def __repr__(self):
        dist = [(t[0], t[1], t[2]) for t in self.routes]
        df = pd.DataFrame(dist, columns=["a", "b", "dist"])
        result1 = df.set_index(["a", "b"]).apply(tuple, axis=1).unstack()

        time = [(t[0], t[1], t[3]) for t in self.routes]
        df = pd.DataFrame(time, columns=["a", "b", "time"])
        result2 = df.set_index(["a", "b"]).apply(tuple, axis=1).unstack()

        return "dist\n" + str(result1) + "\ntime\n" + str(result2)
