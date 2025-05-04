import numpy as np
from model.problem import Problem
from model.input import *


class ProblemInitializer:
    def get_problem(self) -> Problem:
        return Problem(
            self.couriers,
            self.vehicles,
            self.packages,
            self.permissions,
            self.graph,
        )

    def __init__(self):
        n_couriers = 50
        n_vehicles = 50
        n_packages = 50

        self.couriers = [self.random_courier() for _ in range(n_couriers)]

        self.vehicles = [self.random_vehicle() for _ in range(n_vehicles)]

        self.permissions = self.random_permissions(0.7)

        max_address = n_packages
        self.packages = [self.random_package(max_address) for _ in range(n_packages)]
        addresses = np.unique([p.address for p in self.packages])
        for p in self.packages:
            p.address = np.where(p.address == addresses)[0][0] + 1

        self.graph = self.random_graph(len(addresses) + 1, max_coord=50)

    def random_courier(self):
        rate = np.random.randint(100)
        work_limit = np.random.randint(4, 9)
        return Courier(rate, work_limit * 60)

    def random_vehicle(self):
        capacity = np.random.randint(10, 100)
        fuel = np.round(np.random.rand() * 20, 2)
        return Vehicle(capacity, fuel)

    def random_permissions(self, permission_proba):
        n = len(self.couriers)
        m = len(self.vehicles)

        return [
            (i, j)
            for i in range(n)
            for j in range(m)
            if np.random.rand() < permission_proba
        ]

    def random_package(self, max_address, warehouse=0):
        address = np.random.randint(max_address)
        while address == warehouse:
            address = np.random.randint(max_address)

        weight = np.round(np.random.rand() * 10, 2)
        start_time = 0  # np.random.randint(1, 2) * 60
        end_time = np.random.randint(5, 8) * 60
        type = "pickup" if np.random.randint(2) else "delivery"

        return Package(address, weight, start_time, end_time, type)

    def random_graph(self, n_nodes, max_coord=100):
        points = np.random.uniform(0, max_coord, (n_nodes, 2))

        routes = []

        for i, (x, y) in enumerate(points):
            for j, (a, b) in enumerate(points[i + 1 :], start=i + 1):
                dist = np.round(np.sqrt((a - x) ** 2 + (b - y) ** 2), 2)
                time = np.round(dist * (0.5 + np.random.rand()), 2)

                routes.append((i, j, dist, time))

        return Graph(routes, points)
