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
        x_juv = np.zeros((problem.n_vehicles, problem.n_nodes, problem.n_nodes))
        y_kj = np.zeros((problem.n_packages, problem.n_vehicles))
        z_ij = np.zeros((problem.n_couriers, problem.n_vehicles))

        for k in range(self.problem.n_packages):
            j = np.random.randint(self.problem.n_vehicles)
            y_kj[k, j] = 1

        for j in y_kj.sum(axis=0).nonzero()[0]:
            i = np.random.randint(problem.n_couriers)
            tries = 0
            max_tries = 2 * problem.n_couriers
            while (i, j) not in problem.permissions or z_ij[i].sum() >= 1:
                i = np.random.randint(problem.n_couriers)
                tries += 1
                if tries == max_tries:
                    break

            z_ij[i, j] = 1

            vehicle_packages = y_kj[:, j].nonzero()[0]

            vehicle_route = list(
                {
                    p.address
                    for k, p in enumerate(self.problem.packages)
                    if k in vehicle_packages
                }
            )

            vehicle_route = np.random.permutation(vehicle_route)

            x_juv[j, problem.graph.warehouse, vehicle_route[0]] = 1

            for u, v in zip(vehicle_route, vehicle_route[1:]):
                x_juv[j, u, v] = 1

            x_juv[j, vehicle_route[-1], problem.graph.warehouse] = 1

        return Solution(problem, x_juv, y_kj, z_ij)

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
