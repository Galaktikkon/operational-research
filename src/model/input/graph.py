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
        symmetric_data (bool): Set to True if the routes are already symmetric
    """

    def __init__(
        self,
        routes: list[tuple[int, int, float, float]],
        points: np.ndarray,
        warehouse=0,
        symmetric_data = False
    ):
        self.routes = self.__sym(routes) if not symmetric_data else routes
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

    @classmethod
    def from_dict(cls, dictionary):
        points = []
        for point in dictionary["points"]:
            points.append(
                (
                    point["x"],
                    point["y"]
                )
            )
        points = np.array(points)
        
        routes = []
        for route in dictionary["routes"]:
            routes.append(
                (
                    route["start_node"],
                    route["end_node"],
                    route["distance"],
                    route["time"]
                )
            )
        print(routes)
        
        warehouse = dictionary["warehouse"]
            
        return cls(routes, points, warehouse, True)
    
    def to_dict(self):
        points = [
            {"x": float(x), "y": float(y)}
            for x, y in self.points
        ]
        routes = [
            {
                "start_node": int(start_node),
                "end_node": int(end_node),
                "distance": float(distance),
                "time": float(time)
            }
            for start_node, end_node, distance, time in self.routes
        ]
        return {
            "points": points,
            "routes": routes,
            "warehouse": self.warehouse
        }
