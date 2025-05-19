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
        for _ in range(10):
            a, b = self._crossover(s1, s2)
            if a is None and b is None:
                crossnok += 1
            else:
                crossok += 1
                return a, b
        return None, None

    def _crossover(self, s1: Solution, s2: Solution):
        problem = self.problem

        z_j1 = s1.z_j.copy()
        y_k1 = s1.y_k.copy()

        z_j2 = s2.z_j.copy()
        y_k2 = s2.y_k.copy()

        s1_used_couriers = np.unique(z_j1)
        s1_used_couriers = s1_used_couriers[s1_used_couriers != -1]
        s1_unused_couriers = np.setdiff1d(
            np.arange(problem.n_couriers), s1_used_couriers, assume_unique=True
        )

        s2_used_couriers = np.unique(z_j2)
        s2_used_couriers = s2_used_couriers[s2_used_couriers != -1]
        s2_unused_couriers = np.setdiff1d(
            np.arange(problem.n_couriers), s2_used_couriers, assume_unique=True
        )

        s1_used_vehicles = np.unique(y_k1)
        s2_used_vehicles = np.unique(y_k2)

        a_x_jv = s1.x_jv.copy()
        a_y_k = y_k1.copy()
        a_z_j = np.full_like(z_j1, -1)

        b_x_jv = s2.x_jv.copy()
        b_y_k = y_k2.copy()
        b_z_j = np.full_like(z_j2, -1)

        a_set = set()

        s2_used_set = set(s2_used_couriers)
        s2_unused_set = set(s2_unused_couriers)

        b_set = set()

        s1_used_set = set(s1_used_couriers)
        s1_unused_set = set(s1_unused_couriers)

        for j in np.random.permutation(s1_used_vehicles):
            # TODO: sprawdzac czy trasa nie jest dluzsza niz czas pracy kuriera
            for _ in range(2 * len(s2_used_set)):
                i = np.random.choice(list(s2_used_set))
                if (i, j) in problem.permissions and i not in a_set:
                    a_set.add(i)
                    s2_used_set.remove(i)
                    a_z_j[j] = i
                    break
            else:
                for _ in range(2 * len(s2_unused_set)):
                    i = np.random.choice(list(s2_unused_set))
                    if (i, j) in problem.permissions and i not in a_set:
                        a_set.add(i)
                        s2_unused_set.remove(i)
                        a_z_j[j] = i
                        break
                else:
                    break

        for j in np.random.permutation(s2_used_vehicles):
            for _ in range(2 * len(s1_used_set)):
                i = np.random.choice(list(s1_used_set))
                if (i, j) in problem.permissions and i not in b_set:
                    b_set.add(i)
                    s1_used_set.remove(i)
                    b_z_j[j] = i
                    break
            else:
                for _ in range(2 * len(s1_unused_set)):
                    i = np.random.choice(list(s1_unused_set))
                    if (i, j) in problem.permissions and i not in b_set:
                        b_set.add(i)
                        s1_unused_set.remove(i)
                        b_z_j[j] = i
                        break
                else:
                    break

        a = Solution(problem, a_x_jv, a_y_k, a_z_j) if -1 not in a_z_j[a_y_k] else None
        b = Solution(problem, b_x_jv, b_y_k, b_z_j) if -1 not in b_z_j[b_y_k] else None

        if a is not None and not self.checker.is_feasible(a):
            a = None

        if b is not None and not self.checker.is_feasible(b):
            b = None

        return a, b

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

            new = [self.crossover(solutions[i], solutions[j]) for i, j in get_pairs()]
            new = [t[0] for t in new] + [t[1] for t in new]
            new = [n for n in new if n]
            new = [self.mutation(n) for n in new]

            # print("Crossovers", crossok, "/", crossok + crossnok)
            # new = [self.mutation(n) for n in new if n]
            # new = [self.mutation(n) for n in solutions[: l // 2]]
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
