import numpy as np

from model.input import Courier, Package, Vehicle
from model.input.graph import Graph


class Problem:
    """Problem class for the vehicle routing problem with time windows.

    Args
    ----
        couriers (list[Courier]): List of *n* couriers.
        vehicles (list[Vehicle]): List of *m* vehicles.
        packages (list[Package]): List of *f* packages.
        permissions (list[tuple[int, int]]): *r*<sub>i,j</sub> list of permissions for each courier and vehicle. It is a mapping courier -> vehicle.
        graph (Graph): Graph object representing the city network.

    Attributes
    ----------
        couriers (list[Courier]): List of couriers.
        vehicles (list[Vehicle]): List of vehicles.
        packages (list[Package]): List of packages.
        permissions (list[tuple[int, int]]): List of permissions for each courier and vehicle. It is a mapping courier -> vehicle.
        graph (Graph): Graph object representing the city network.
        n_couriers (int): Number of couriers.
        n_vehicles (int): Number of vehicles.
        n_packages (int): Number of packages.
        n_nodes (int): Number of nodes in the graph.
        s_uv (np.ndarray): Matrix mapping the time taken to travel from node u to node v.
        g_uv (np.ndarray): Matrix mapping the distance taken to travel from node u to node v.
    """

    def __init__(
        self,
        couriers: list[Courier],
        vehicles: list[Vehicle],
        packages: list[Package],
        permissions: list[tuple[int, int]],
        graph: Graph,
    ):
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
        """Calculates the *s*<sub>uv</sub> and *g*<sub>uv</sub>  matrices for the problem:
        - *s*<sub>uv</sub> maps the time taken to travel from node *u* to node *v*,
        - *g*<sub>uv</sub> maps the distance taken to travel from node *u* to node *v*.
        """
        n_nodes = self.graph.n_nodes

        self.s_uv = np.zeros((n_nodes, n_nodes))
        self.g_uv = np.zeros((n_nodes, n_nodes))

        for u, v, dist, time in self.graph.routes:
            self.s_uv[u, v] = time
            self.g_uv[u, v] = dist
