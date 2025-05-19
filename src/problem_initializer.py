import numpy as np

from model import Graph
from model.input import Courier, Package, Vehicle
from model.problem import Problem


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

    def get_problem(self) -> Problem:
        return Problem(
            self.couriers,
            self.vehicles,
            self.packages,
            self.permissions,
            self.graph,
        )

    def __init__(self, n_couriers, n_vehicles, n_packages):
        self.couriers = [self.random_courier() for _ in range(n_couriers)]

        self.vehicles = [self.random_vehicle() for _ in range(n_vehicles)]

        self.permissions = self.random_permissions(1)

        max_address = n_packages
        self.packages = [self.random_package(max_address) for _ in range(n_packages)]
        addresses = np.unique([p.address for p in self.packages])
        for p in self.packages:
            p.address = np.where(p.address == addresses)[0][0] + 1

        self.graph = self.random_graph(len(addresses) + 1, max_coord=50)

    def random_courier(self):
        """
        Generate a random courier with a random rate and work limit.

        Returns
        -------
            Courier: A courier object with random rate and work limit.
        """
        rate = np.random.randint(100)
        work_limit = 1e10  # 8  # np.random.randint(4, 9)
        return Courier(rate, work_limit * 60)

    def random_vehicle(self):
        """
        Generate a random vehicle with a random capacity and fuel.

        Returns
        -------
            Vehicle: A vehicle object with random capacity and fuel.
        """
        capacity = 1e10  # np.random.randint(10, 100)
        fuel = np.round(np.random.rand() * 20, 2)
        return Vehicle(capacity, fuel)

    def random_permissions(self, permission_proba):
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
            if np.random.rand() <= permission_proba
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

        weight = np.round(np.random.rand() * 10, 2)
        start_time = 0  # np.random.randint(1, 2) * 60
        end_time = 1e10  # 8 * 60  # np.random.randint(5, 9) * 60
        type = "pickup" if np.random.randint(2) else "delivery"

        return Package(address, weight, start_time, end_time, type)

    def random_graph(self, n_nodes, max_coord=100):
        """
        Generate a random graph with nodes and edges.

        Args
        ----
            n_nodes (int): Number of nodes in the graph.
            max_coord (int): Maximum coordinate value for the nodes.

        Returns
        -------
            Graph: A graph object with nodes and edges.
        """
        points = np.random.uniform(0, max_coord, (n_nodes, 2))

        routes = []

        for i, (x, y) in enumerate(points):
            for j, (a, b) in enumerate(points[i + 1 :], start=i + 1):
                dist = np.round(np.sqrt((a - x) ** 2 + (b - y) ** 2), 2)
                time = dist  # np.round(dist * (0.5 + np.random.rand()), 2)

                routes.append((i, j, dist, time))

        return Graph(routes, points)
