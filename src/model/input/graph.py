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

        self.dist = {(u, v): d for (u, v, d, _) in self.routes}
        self.time = {(u, v): t for (u, v, _, t) in self.routes}

        self.points = points

    def __repr__(self):
        df = pd.DataFrame(self.routes, columns=["a", "b", "dist", "time"])

        dist = df.pivot(index="a", columns="b", values="dist").to_string()
        time = df.pivot(index="a", columns="b", values="time").to_string()

        return f"dist\n{dist}\n\ntime\n{time}"
