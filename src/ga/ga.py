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

        x_jv = np.full_like(s1.x_jv, warehouse)
        y_k = np.full_like(y_k1, -1)
        z_j = np.full_like(z_j1, -1)

        vehicles_intersection = np.intersect1d(y_k1, y_k2)
        vehicles_symdiff = np.setdiff1d(
            np.union1d(y_k1, y_k2), vehicles_intersection, assume_unique=True
        )
        vehicles_remaining = np.setdiff1d(
            np.arange(self.problem.n_vehicles),
            np.union1d(y_k1, y_k2),
            assume_unique=True,
        )
        vehicle_arrays = [vehicles_intersection, vehicles_symdiff, vehicles_remaining]

        couriers_intersection = np.intersect1d(z_j1, z_j2, assume_unique=True)
        couriers_intersection = couriers_intersection[couriers_intersection != -1]
        couriers_symdiff = np.setdiff1d(
            np.union1d(z_j1, z_j2), couriers_intersection, assume_unique=True
        )
        couriers_symdiff = couriers_symdiff[couriers_symdiff != -1]
        couriers_remaining = np.setdiff1d(
            np.arange(self.problem.n_couriers), np.union1d(z_j1, z_j2)
        )
        courier_arrays = [couriers_intersection, couriers_symdiff, couriers_remaining]

        def get_rnd(arr):
            if not arr[2].size:
                if not arr[1].size:
                    return np.random.choice(arr[0])

                ix = np.random.choice([0, 1], p=[0.7, 0.3])
                return np.random.choice(arr[ix])

            ix = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
            return np.random.choice(arr[ix])

        capacity = {j: 0 for j in range(problem.n_vehicles)}

        for k, p in enumerate(problem.packages):
            while y_k[k] == -1:
                j = get_rnd(vehicle_arrays)
                if capacity[j] + p.weight <= problem.vehicles[j].capacity:
                    capacity[j] += p.weight
                    y_k[k] = j
                    x_jv[j] = calculate_vehicle_route(problem, y_k, j)

        vs = np.hstack([np.random.permutation(arr) for arr in vehicle_arrays])

        for j in vs:
            while z_j[j] == -1:
                i = get_rnd(courier_arrays)
                if (i, j) in problem.permissions:
                    z_j[j] = i

        # TODO: problem, trasy są od nowa losowo

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

            # print("Crossovers", crossok, "/", crossok + crossnok)
            # new = [self.mutation(n) for n in new if n]
            new = [self.mutation(n) for n in solutions[: l // 2]]
            o = 0
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
