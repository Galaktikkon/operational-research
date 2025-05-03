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
        self.couriers = [self.random_courier() for _ in range(20)]

        self.vehicles = [self.random_vehicle() for _ in range(15)]

        self.permissions = self.full_permissions()

        routes = [
            (0, 1, 1, 60),
            (0, 2, 1, 60),
            (0, 3, 1, 60),
            (1, 2, 1, 60),
            (1, 3, 1, 60),
            (2, 3, 1, 60),
        ]
        self.graph = Graph(routes)

        self.packages = [self.random_package() for _ in range(5)]

    def random_courier(self):
        rate = np.random.randint(100)
        work_limit = np.random.randint(9)
        return Courier(rate, work_limit * 60)

    def random_vehicle(self):
        capacity = np.random.randint(100)
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
        start_time = 0
        end_time = 8 * 60
        type = "delivery"

        return Package(address, weight, start_time, end_time, type)
