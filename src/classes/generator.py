import math
from typing import Dict, List, Optional, Set, Tuple
from classes.checker import Checker
from classes.problem_instance import ProblemInstance
from classes.solution import Solution
import sys


class Generator:
    def generate_random_solution(problem: ProblemInstance) -> Optional[Solution]:
        courier_ids = list(problem.couriers.keys())
        vehicle_ids = list(problem.vehicles.keys())
        package_ids = list(problem.packages.keys())

        z_ij: Dict[Tuple[int, int], int] = {}
        y_kj: Dict[Tuple[int, int], int] = {}
        routes: Dict[int, List[int]] = {
            vid: [problem.warehouse_node] for vid in vehicle_ids
        }
        v_k: Dict[int, float] = {}

        courier_assigned = {cid: False for cid in courier_ids}
        vehicle_used = {vid: False for vid in vehicle_ids}
        package_assigned = {pid: False for pid in package_ids}

        # 1. Assign couriers to vehicles
        for cid in courier_ids:
            if not courier_assigned[cid]:
                for vid in vehicle_ids:
                    if (
                        not vehicle_used[vid]
                        and problem.permissions.get((cid, vid), 0) == 1
                    ):
                        z_ij[(cid, vid)] = 1
                        courier_assigned[cid] = True
                        vehicle_used[vid] = True
                        break
            if not courier_assigned[cid]:
                return None

        # 2. Assign packages to vehicles
        vehicle_packages: Dict[int, List[int]] = {vid: [] for vid in vehicle_ids}
        for vid in vehicle_ids:
            current_capacity = problem.vehicles[vid].capacity
            for pid in package_ids:
                if not package_assigned[pid] and y_kj.get((pid, vid), 0) == 0:
                    if problem.packages[pid].weight <= current_capacity:
                        vehicle_packages[vid].append(pid)
                        y_kj[(pid, vid)] = 1
                        package_assigned[pid] = True
                        current_capacity -= problem.packages[pid].weight

        # 3. create routes
        for vid, assigned_pids in vehicle_packages.items():
            current_route = [problem.warehouse_node]
            current_time = 0.0
            for pid in assigned_pids:
                address = problem.packages[pid].address
                travel_time = problem.travel_times.get(
                    (current_route[-1], address), 0.0
                )
                current_time += travel_time
                current_route.append(address)
                v_k[pid] = current_time
            current_route.append(problem.warehouse_node)
            routes[vid] = current_route

        # 4. Calculate distances
        t_i: Dict[int, float] = {}
        for (cid, vid), assigned in z_ij.items():
            if assigned == 1:
                route_time = 0.0
                if routes.get(vid):
                    for i in range(len(routes[vid]) - 1):
                        u = routes[vid][i]
                        v = routes[vid][i + 1]
                        route_time += problem.travel_times.get((u, v), 0.0)
                t_i[cid] = route_time

        return Solution(problem, z_ij, y_kj, routes, v_k)

    def get_solution_signature(solution: Solution) -> tuple:
        route_items = tuple(sorted((k, tuple(v)) for k, v in solution.routes.items()))
        z_items = tuple(sorted(solution.z_ij.items()))
        y_items = tuple(sorted(solution.y_kj.items()))
        return (route_items, z_items, y_items)

    def generate_many_feasible(
        problem: ProblemInstance,
        num_to_find: int,
        max_attempts_initial: Optional[int | None] = None,
    ) -> List[Solution]:
        feasible_solutions: List[Solution] = []
        found_signatures: Set[tuple] = set()
        attempts_initial = 0

        if not max_attempts_initial:
            max_attempts_initial = math.inf

        while (
            len(feasible_solutions) < num_to_find
            and attempts_initial < max_attempts_initial
        ):
            attempts_initial += 1

            sys.stdout.write(
                f"\rAttempts: {attempts_initial}/{max_attempts_initial} | Solutions found: {len(feasible_solutions)}"
            )
            sys.stdout.flush()

            candidate = Generator.generate_random_solution(problem)
            if candidate:
                is_feasible_sol, _ = Checker.is_feasible(candidate)
                if is_feasible_sol:
                    signature = Generator.get_solution_signature(candidate)
                    if signature not in found_signatures:
                        feasible_solutions.append(candidate)
                        found_signatures.add(signature)

        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

        return feasible_solutions
