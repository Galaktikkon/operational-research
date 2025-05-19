from copy import deepcopy

import numpy as np
import pandas as pd


class Graph:
    """
    Graph class representing a city network.

    Args
    ----
        routes (list[tuple[int, int, float, float]]): List of routes represented as tuples (start_node, end_node, distance, time).
        points (np.ndarray): Array of coordinates for the nodes in the graph.
        warehouse (int): Identifier for the warehouse node. Defaults to 0.
    """

    def __init__(
        self,
        routes: list[tuple[int, int, float, float]],
        points: np.ndarray,
        warehouse=0,
    ):
        self.routes = self.__sym(routes)
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

    def __sym(self, routes: list[tuple[int, int, float, float]]):
        """
        Augment the routes to include symmetric routes.

        Args
        ----
            routes (list[tuple[int, int, float, float]]): List of routes represented as tuples (start_node, end_node, distance, time).

        Returns
        -------
            list[tuple[int, int, float, float]]: Symmetric routes including original and reverse routes.
        """

        original = deepcopy(routes)
        symmetrical = [(b, a, dist, time) for a, b, dist, time in original]

        nodes = {t[0] for t in original} | {t[1] for t in original}

        return original + symmetrical + [(a, a, 0, 0) for a in nodes]
