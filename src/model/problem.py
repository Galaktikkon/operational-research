import numpy as np
from model.input import *


class Problem:
    """
    permissions : list[(courier, vehicle)]
    """

    def __init__(
        self,
        couriers: list[Courier],
        vehicles: list[Vehicle],
        packages: list[Package],
        permissions: list[tuple[int, int]],
        graph: Graph,
    ):
        """
        permissions : list[(courier, vehicle)]
        """
        self.couriers = couriers
        self.vehicles = vehicles
        self.packages = packages

        self.permissions = permissions
        self.graph = graph

        self.n_couriers = len(couriers)
        self.n_vehicles = len(vehicles)
        self.n_packages = len(packages)
        self.n_nodes = graph.n_nodes

        self._calc_s_uv_g_uv()

    def __repr__(self):
        rows = (
            ["Couriers"]
            + [
                f"{i}: {str(c)} {[t[1] for t in self.permissions if t[0] == i]}"
                for i, c in enumerate(self.couriers)
            ]
            + ["\nVehicles"]
            + [f"{j}: {str(v)}" for j, v in enumerate(self.vehicles)]
            + ["\nPackages"]
            + [f"{k}: {str(p)}" for k, p in enumerate(self.packages)]
            + ["\nGraph"]
            + [str(self.graph)]
            + [""]
        )
        return "\n".join(rows)

    def _calc_s_uv_g_uv(self):
        n_nodes = self.graph.n_nodes

        self.s_uv = np.zeros((n_nodes, n_nodes))
        self.g_uv = np.zeros((n_nodes, n_nodes))

        for u, v, dist, time in self.graph.routes:
            self.s_uv[u, v] = time
            self.g_uv[u, v] = dist
