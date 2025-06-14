import sys
from typing import Optional

import numpy as np

from model.problem import Problem
from model.solution import Solution
from solution_checker import SolutionChecker
from utils import calculate_vehicle_route


class Generator:
    """Class to generate feasible solutions for the problem.
    Args
    ----
        problem (Problem): The problem to generate solutions for.
    """

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
            # if all couriers are already assigned to vehicles
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
        """
        Assign a courier to a vehicle. The courier is chosen randomly from the
        list of couriers that are allowed to be assigned to the vehicle.

        Args
        ----
            j (int): The vehicle to which the courier is assigned.

        """
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
        self.x_jv[j] = calculate_vehicle_route(self.problem, self.y_k, j)

    def generate_many_feasible(
        self,
        num_to_find=int(1e6),
        max_attempts=int(1e6),
        verbose=True,
    ) -> list[Solution]:
        feasible_solutions = set()
        attempts = 0

        while len(feasible_solutions) < num_to_find and attempts < max_attempts:
            attempts += 1

            if verbose:
                sys.stdout.write(
                    f"\rAttempts: {attempts}/{max_attempts} | Solutions found: {len(feasible_solutions)}"
                )
                sys.stdout.flush()

            candidate = self.generate_solution()
            if candidate and self.checker.is_feasible(candidate):
                if candidate not in feasible_solutions:
                    feasible_solutions.add(candidate)

        if verbose:
            sys.stdout.write(
                f"\rAttempts: {attempts}/{max_attempts} | Solutions found: {len(feasible_solutions)}"
            )
            sys.stdout.flush()
            print()

        return list(feasible_solutions)
