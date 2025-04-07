import random
from typing import List, Optional, Set
from classes.checker import Checker
from classes.problem_instance import ProblemInstance
from classes.solution import Solution


class Generator:
    def generate_random_solution(problem: ProblemInstance) -> Optional[Solution]:
        n = problem.n
        m = problem.m
        courier_ids = list(problem.couriers.keys())
        vehicle_ids = list(problem.vehicles.keys())
        package_ids = list(problem.packages.keys())

        if n == 0 or m == 0:
            print("No couriers or vehicles available.")
            return None

        z_ij = {}
        for i in courier_ids:
            for j in vehicle_ids:
                z_ij[(i, j)] = random.randint(0, 1)

        y_kj = {}
        for k in package_ids:
            for j in vehicle_ids:
                y_kj[(k, j)] = random.randint(0, 1)

        routes = {
            j: [problem.warehouse_node]
            + random.sample(
                list(problem.packages.values()),
                random.randint(0, len(problem.packages)),
            )
            + [problem.warehouse_node]
            for j in vehicle_ids
        }

        v_k = {
            k: random.uniform(
                problem.packages[k].start_time, problem.packages[k].end_time
            )
            if problem.packages
            else 0
            for k in package_ids
        }

        try:
            solution = Solution(problem, z_ij, y_kj, routes, v_k)
            return solution
        except Exception as e:
            print(f"Błąd podczas tworzenia obiektu Solution: {e}")
            return None

    def get_solution_signature(solution: Solution) -> tuple:
        route_items = tuple(
            sorted((k, tuple(n.id for n in v)) for k, v in solution.routes.items())
        )
        z_items = tuple(sorted(solution.z_ij.items()))
        y_items = tuple(sorted(solution.y_kj.items()))
        return (route_items, z_items, y_items)

    def generate_many_feasible(
        problem: ProblemInstance,
        num_to_find: int,
        max_attempts_initial: int,
    ) -> List[Solution]:
        feasible_solutions: List[Solution] = []
        found_signatures: Set[tuple] = set()
        attempts_initial = 0

        while (
            len(feasible_solutions) < num_to_find
            and attempts_initial < max_attempts_initial
        ):
            attempts_initial += 1

            candidate = Generator.generate_random_solution(problem)
            if candidate:
                is_feasible_sol, errors = Checker.is_feasible(candidate)
                if is_feasible_sol:
                    signature = Generator.get_solution_signature(candidate)
                    if signature not in found_signatures:
                        feasible_solutions.append(candidate)
                        found_signatures.add(signature)

        return feasible_solutions
