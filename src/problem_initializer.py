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
        self.couriers = [self.random_courier() for _ in range(5)]

        self.vehicles = [self.random_vehicle() for _ in range(5)]

        self.permissions = self.full_permissions()

        routes = self.random_routes(20)
        self.graph = Graph(routes)

        self.packages = [self.random_package() for _ in range(20)]

    def random_courier(self):
        rate = np.random.randint(100)
        work_limit = np.random.randint(4, 9)
        return Courier(rate, work_limit * 60)

    def random_vehicle(self):
        capacity = np.random.randint(10, 100)
        fuel = np.round(np.random.rand() * 20, 2)
        return Vehicle(capacity, fuel)

    def full_permissions(self):
        n = len(self.couriers)
        m = len(self.vehicles)

        return [(i, j) for i in range(n) for j in range(m)]

    def random_package(self):
        n_nodes = self.graph.n_nodes

        address = np.random.randint(n_nodes)
        while address == self.graph.warehouse:
            address = np.random.randint(n_nodes)

        weight = np.round(np.random.rand() * 10, 2)
        start_time = 0  # np.random.randint(1, 2) * 60
        end_time = np.random.randint(5, 8) * 60
        type = "pickup" if np.random.randint(2) else "delivery"

        return Package(address, weight, start_time, end_time, type)

    def random_routes(self, n_nodes):
        points = np.random.uniform(0, 100, (n_nodes, 2))

        routes = []

        for i, (x, y) in enumerate(points):
            for j, (a, b) in enumerate(points[i + 1 :], start=i + 1):
                dist = np.round(np.sqrt((a - x) ** 2 + (b - y) ** 2), 2)
                time = np.round(dist * (0.5 + np.random.rand()), 2)

                routes.append((i, j, dist, time))

        return routes
