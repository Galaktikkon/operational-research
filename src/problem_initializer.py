from model.problem import Problem
from model.input import *


class ProblemInitializer:
    def get_problem(self) -> Problem:
        return Problem(
            self._couriers,
            self._vehicles,
            self._packages,
            self._permissions,
            Graph(self._routes),
        )

    def __init__(self):
        self._couriers = [Courier(20, 8 * 60)]

        self._vehicles = [
            Vehicle(100, 1),
            Vehicle(100, 1),
            Vehicle(100, 1),
            Vehicle(100, 1),
        ]

        self._packages = [Package(1, 1, 0, 8 * 60)]

        self._permissions = [
            (0, 0),
            # (0, 1),
            # (0, 2),
            # (0, 3),
            # (1, 0),
            # (1, 1),
            # (1, 2),
            # (1, 3),
            # (2, 0),
            # (2, 1),
            # (2, 2),
            # (2, 3),
            # (3, 0),
            # (3, 1),
            # (3, 2),
            (3, 3),
        ]

        self._routes = [
            (0, 1, 1, 60),
            (0, 2, 1, 60),
            (0, 3, 1, 60),
            (1, 2, 1, 60),
            (1, 3, 1, 60),
            (2, 3, 1, 60),
        ]
