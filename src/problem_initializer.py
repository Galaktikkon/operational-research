import json

import numpy as np

from model import Graph
from model.input import Courier, Package, Vehicle
from model.problem import Problem


def randf(start, end):
    return np.random.rand() * (end - start) + start


def randi(start, end):
    if start == end:
        return start
    return np.random.randint(start, end)


class ProblemInitializer:
    """Class to generate a problem instance for the vehicle routing problem.

    Args
    ----
        n_couriers (int): Number of couriers.
        n_vehicles (int): Number of vehicles.
        n_packages (int): Number of packages.

    Methods
    -------
        get_problem() -> Problem:
            Returns a problem instance with the generated couriers, vehicles, packages, permissions, and graph.
        random_courier() -> Courier:
            Generates a random courier with a random rate and work limit.
        random_vehicle() -> Vehicle:
            Generates a random vehicle with a random capacity and fuel.
        random_permissions(permission_proba: float) -> List[Tuple[int, int]]:
            Generates random permissions for couriers and vehicles.
        random_package(max_address: int) -> Package:
            Generates a random package with a random address, weight, start time, end time, and type.
        random_graph(n_nodes: int, max_coord: int = 100) -> Graph:
            Generates a random graph with nodes and edges.
    """

    def __init__(
        self,
        n_couriers,
        n_vehicles,
        n_packages,
        graph_max_coord=50,
        rate_range=(0, 100),
        work_limit_range=(int(1e10), int(1e10)),
        capacity_range=(int(1e10), int(1e10)),
        fuel_range=(0, 20),
        weight_range=(0, 10),
        package_start_time_range=(0, 0),
        package_end_time_range=(int(1e10), int(1e10)),
        time_dist_coeff=0.5,
        permission_proba=1,
        pickup_delivery_proba=0.5,
    ):
        self.n_couriers = n_couriers
        self.n_vehicles = n_vehicles
        self.n_packages = n_packages
        self.graph_max_coord = graph_max_coord
        self.rate_range = rate_range
        self.work_limit_range = work_limit_range
        self.capacity_range = capacity_range
        self.fuel_range = fuel_range
        self.weight_range = weight_range
        self.package_start_time_range = package_start_time_range
        self.package_end_time_range = package_end_time_range
        self.time_dist_coeff = time_dist_coeff
        self.permission_proba = permission_proba
        self.pickup_delivery_proba = pickup_delivery_proba

        self.couriers = []
        self.vehicles = []
        self.permissions = []
        self.packages = []
        self.graph = None

    def get_problem(self) -> Problem:
        return Problem(
            self.couriers,
            self.vehicles,
            self.packages,
            self.permissions,
            self.graph,
        )

    def generate_random(self):
        self.couriers = [self.random_courier() for _ in range(self.n_couriers)]

        self.vehicles = [self.random_vehicle() for _ in range(self.n_vehicles)]

        self.permissions = self.random_permissions()

        max_address = self.n_packages
        self.packages = [
            self.random_package(max_address) for _ in range(self.n_packages)
        ]
        addresses = np.unique([p.address for p in self.packages])
        for p in self.packages:
            p.address = np.where(p.address == addresses)[0][0] + 1

        self.graph = self.random_graph(len(addresses) + 1)

    def random_courier(self):
        """
        Generate a random courier with a random rate and work limit.

        Returns
        -------
            Courier: A courier object with random rate and work limit.
        """
        rate = randi(*self.rate_range)
        work_limit = randi(*self.work_limit_range)
        return Courier(rate, work_limit * 60)

    def random_vehicle(self):
        """
        Generate a random vehicle with a random capacity and fuel.

        Returns
        -------
            Vehicle: A vehicle object with random capacity and fuel.
        """
        capacity = randi(*self.capacity_range)
        fuel = np.round(randf(*self.fuel_range), 2)
        return Vehicle(capacity, fuel)

    def random_permissions(self):
        """
        Generate random permissions for couriers and vehicles.

        Args
        ----
            permission_proba (float): Probability of a courier being assigned to a vehicle.
        Returns
        -------
            List[Tuple[int, int]]: List of tuples representing the permissions.
        """
        n = len(self.couriers)
        m = len(self.vehicles)

        return [
            (i, j)
            for i in range(n)
            for j in range(m)
            if np.random.rand() <= self.permission_proba
        ]

    def random_package(self, max_address):
        """
        Generate a random package with a random address, weight, start time, end time, and type.

        Args
        ----
            max_address (int): Maximum address value for the package.

        Returns
        -------
            Package: A package object with random address, weight, start time, end time, and type.
        """

        address = np.random.randint(max_address)

        weight = np.round(randf(*self.weight_range), 2)
        start_time = randi(*self.package_start_time_range) * 60
        end_time = randi(*self.package_end_time_range) * 60
        type = "pickup" if np.random.rand() < self.pickup_delivery_proba else "delivery"

        return Package(address, weight, start_time, end_time, type)

    def random_graph(self, n_nodes):
        """
        Generate a random graph with nodes and edges.

        Args
        ----
            n_nodes (int): Number of nodes in the graph.

        Returns
        -------
            Graph: A graph object with nodes and edges.
        """
        points = np.random.uniform(0, self.graph_max_coord, (n_nodes, 2))

        routes = []

        for i, (x, y) in enumerate(points):
            for j, (a, b) in enumerate(points[i + 1 :], start=i + 1):
                dist = np.round(np.sqrt((a - x) ** 2 + (b - y) ** 2), 2)
                time = np.round(dist * (1 - self.time_dist_coeff + np.random.rand()), 2)

                routes.append((i, j, dist, time))

        return Graph(routes, points)
