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

    def __repr__(self):
        rows = (
            ["Couriers"]
            + [f"{i}: {str(c)}" for i, c in enumerate(self.couriers)]
            + ["\nVehicles"]
            + [f"{j}: {str(v)}" for j, v in enumerate(self.vehicles)]
            + ["\nPackages"]
            + [f"{k}: {str(p)}" for k, p in enumerate(self.packages)]
            + ["\nGraph"]
            + [str(self.graph)]
            + [""]
        )
        return "\n".join(rows)
