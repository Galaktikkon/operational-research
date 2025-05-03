from model.input import *


class Problem:
    """
    permissions : list[(courier_ix, vehicle_ix)]
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

    def __repr__(self):
        rows = (
            ["Couriers"]
            + [str(c) for c in self.couriers]
            + ["\nVehicles"]
            + [str(v) for v in self.vehicles]
            + ["\nPackages"]
            + [str(p) for p in self.packages]
            + [""]
        )
        return "\n".join(rows)
