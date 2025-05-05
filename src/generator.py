import sys
from typing import Optional
from solution_checker import SolutionChecker
from model.problem import Problem
from model.solution import Solution
import numpy as np


class Generator:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.checker = SolutionChecker(problem)

    def generate_solution(self) -> Optional[Solution]:
        problem = self.problem
        warehouse = self.problem.graph.warehouse
        self.x_jv = np.full(
            (problem.n_vehicles, problem.n_nodes + 1), warehouse, dtype=int
        )
        self.y_k = np.full(problem.n_packages, -1, dtype=int)
        self.z_j = np.full(problem.n_vehicles, -1, dtype=int)

        x_jv, y_k, z_j = self.x_jv, self.y_k, self.z_j

        matched_vehicles = set()

        for k in range(problem.n_packages):
            if np.unique(z_j[z_j != -1]).size == problem.n_couriers:
                y_k[k] = np.random.choice(list(matched_vehicles))
            else:
                y_k[k] = np.random.randint(problem.n_vehicles)

            if y_k[k] not in matched_vehicles:
                self._add_courier_to_vehicle(y_k[k])
                matched_vehicles.add(y_k[k])

        for j in np.unique(y_k):
            self._add_route_to_vehicle(j)

        return Solution(problem, x_jv, y_k, z_j)

    def _add_courier_to_vehicle(self, j):
        problem = self.problem
        i = np.random.randint(problem.n_couriers)
        tries = 0
        max_tries = 2 * problem.n_couriers
        while (i, j) not in problem.permissions or i in self.z_j:
            i = np.random.randint(problem.n_couriers)
            tries += 1
            if tries == max_tries:
                break

        self.z_j[j] = i

    def _add_route_to_vehicle(self, j):
        vehicle_packages = np.where(self.y_k == j)[0]

        vehicle_route = np.unique(
            [
                p.address
                for k, p in enumerate(self.problem.packages)
                if k in vehicle_packages
            ]
        )

        vehicle_route = np.random.permutation(vehicle_route)

        for v_i, v in enumerate(vehicle_route, start=1):
            self.x_jv[j, v_i] = v

    def generate_many_feasible(
        self,
        num_to_find=int(1e6),
        max_attempts=int(1e6),
    ) -> list[Solution]:
        feasible_solutions = set()
        attempts = 0

        while len(feasible_solutions) < num_to_find and attempts < max_attempts:
            attempts += 1

            sys.stdout.write(
                f"\rAttempts: {attempts}/{max_attempts} | Solutions found: {len(feasible_solutions)}"
            )
            sys.stdout.flush()

            candidate = self.generate_solution()
            if candidate and self.checker.is_feasible(candidate):
                if candidate not in feasible_solutions:
                    feasible_solutions.add(candidate)

        print()

        return list(feasible_solutions)
