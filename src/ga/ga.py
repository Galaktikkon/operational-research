import sys
from utils import *
import numpy as np
from model.solution import Solution
from model.problem import Problem
from solution_checker import SolutionChecker
import functools
from copy import deepcopy
from .mutations import *

crossok = 0
crossnok = 0


class GA:
    def __init__(self, problem: Problem, initial_population: list[Solution]):
        self.problem = problem
        self.checker = SolutionChecker(problem)
        self.C = 1
        self.alpha = 0
        self.initial_population = initial_population

    @functools.cache
    def get_cost(self, solution: Solution):
        c_i = np.array([c.hourly_rate / 60 for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.get_t_i() @ c_i
        fuel_cost = self.C * (p_j @ solution.get_d_j())
        delay = self.alpha / self.problem.n_packages * np.sum(solution.get_v_k() - a_k)

        return rates + fuel_cost + delay

    def crossover(self, s1: Solution, s2: Solution):
        global crossok, crossnok
        for _ in range(100):
            s = self._crossover(s1, s2)
            if s is not None:
                crossok += 1
                return s
            else:
                crossnok += 1
        return None

    def _crossover(self, s1: Solution, s2: Solution):
        problem = self.problem
        warehouse = problem.graph.warehouse
        z_j1 = s1.z_j.copy()
        y_k1 = s1.y_k.copy()

        z_j2 = s2.z_j.copy()
        y_k2 = s2.y_k.copy()

        used_vehicles = np.unique(np.append(y_k1, y_k2))
        unused_vehicles = np.setdiff1d(
            np.arange(self.problem.n_vehicles), used_vehicles
        )
        vehicles = used_vehicles if used_vehicles.size else unused_vehicles

        used_couriers = np.unique(np.append(z_j1, z_j2))
        unused_couriers = np.setdiff1d(
            np.arange(self.problem.n_couriers), used_couriers
        )

        x_jv = np.full((problem.n_vehicles, problem.n_nodes + 1), warehouse, dtype=int)
        y_k = np.full(problem.n_packages, -1, dtype=int)
        z_j = np.full(problem.n_vehicles, -1, dtype=int)

        for k in range(self.problem.n_packages):
            y_k[k] = np.random.choice(vehicles)

        for j in np.unique(y_k):
            for _ in range(100):
                i = np.random.choice(used_couriers)
                if i not in z_j:
                    z_j[j] = i
                    break
            else:
                i = np.random.choice(unused_couriers)
                while i in z_j:
                    i = np.random.choice(unused_couriers)
                z_j[j] = i

            x_jv[j] = calculate_vehicle_route(problem, y_k, j)

        s = Solution(problem, x_jv, y_k, z_j)

        return s if self.checker.is_feasible(s) else None

    def mutation(self, solution: Solution):
        x_jv = solution.x_jv
        y_k = solution.y_k
        z_j = solution.z_j

        solution = Solution(solution.problem, x_jv.copy(), y_k.copy(), z_j.copy())
        original = Solution(solution.problem, x_jv.copy(), y_k.copy(), z_j.copy())

        mutations = [
            CouriersMutation(solution),
            PackagesMutation(solution),
            UsedVehiclesMutation(solution),
            UnusedVehiclesMutation(solution),
        ] + [RouteMutation(solution, j) for j in np.random.permutation(np.unique(y_k))]

        mutation_order = np.random.permutation(np.arange(len(mutations)))

        for m in mutation_order:
            mutation: Mutation = mutations[m]

            if not mutation.is_possible():
                continue

            mutation.mutate_solution()
            assert solution != original

            if self.checker.is_feasible(solution):
                return solution
            else:
                mutation.reverse()
                assert solution == original

        return solution

    def run(self, max_iter=1000):
        solutions = self.initial_population
        l = len(solutions)

        solutions.sort(key=lambda s: self.get_cost(s))
        initial_best = deepcopy(solutions[0])

        pairs = [(i, j) for i in range(l // 2) for j in range(i + 1, l // 2)]

        def get_pairs():
            index = np.random.randint(low=0, high=len(pairs), size=(l // 2))
            return [pairs[i] for i in index]

        for i in range(1, max_iter + 1):
            solutions.sort(key=lambda s: self.get_cost(s))

            # new = [self.crossover(solutions[i], solutions[j]) for i, j in get_pairs()]
            # new = [self.mutation(n) for n in new if n]
            new = [self.mutation(n) for n in solutions[: l // 2]]
            o = 1
            while len(new) < l // 2:
                new.append(solutions[l // 2 + o])
                o += 1

            solutions = solutions[: l // 2] + new

            sys.stdout.write("\r" + " " * 80 + "\r" + str(i))
            sys.stdout.flush()

        solutions.sort(key=lambda s: self.get_cost(s))
        print()

        print("Crossovers", crossok, "/", crossok + crossnok)

        mutations = [
            CouriersMutation,
            PackagesMutation,
            UsedVehiclesMutation,
            UnusedVehiclesMutation,
            RouteMutation,
        ]

        m: Mutation
        for m in mutations:
            print(m.__name__, m.times_feasible_created, "/", m.times_run)

        return initial_best, solutions[0]
