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
