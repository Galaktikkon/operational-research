import sys
from utils import *
import numpy as np
from model.solution import Solution
from model.problem import Problem
from solution_checker import SolutionChecker
import functools
from copy import deepcopy


class GA:
    def __init__(self, problem: Problem, initial_population: list[Solution]):
        self.problem = problem
        self.checker = SolutionChecker(problem)
        self.C = 1
        self.alpha = 0
        self.initial_population = initial_population

    @functools.cache
    def get_score(self, solution: Solution):
        c_i = np.array([c.hourly_rate / 60 for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.get_t_i() @ c_i
        fuel_cost = self.C * (p_j @ solution.get_d_j())
        delay = self.alpha / self.problem.n_packages * np.sum(solution.get_v_k() - a_k)

        return rates + fuel_cost + delay

    def crossover(self, s1: Solution, s2: Solution):
        for _ in range(100):
            s = self._crossover(s1, s2)
            if s is not None:
                return s
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
        z_j = solution.z_j.copy()
        x_jv = solution.x_jv.copy()
        y_k = solution.y_k.copy()

        # zamiana losowych kurierow
        if np.random.rand() < 0.5:
            i1 = np.random.randint(self.problem.n_couriers)
            i2 = np.random.randint(self.problem.n_couriers)
            while self.problem.n_couriers > 1 and i1 == i2:
                i2 = np.random.randint(self.problem.n_couriers)

            j1 = np.where(z_j == i1)[0]
            j1 = j1[0] if j1.size else None

            j2 = np.where(z_j == i2)[0]
            j2 = j2[0] if j2.size else None

            if j1 is not None:
                z_j[j1] = i2
            if j2 is not None:
                z_j[j2] = i1

            s = Solution(self.problem, x_jv, y_k, z_j)
            if self.checker.is_feasible(s):
                return s
            else:
                return solution
                if j1 is not None:
                    z_j[j1] = i1
                if j2 is not None:
                    z_j[j2] = i2

        # przeniesienie paczki
        if np.random.rand() < 0.5 and self.problem.n_packages >= 2:
            k = np.random.randint(self.problem.n_packages)
            for _ in range(100):
                j = np.random.randint(self.problem.n_vehicles)
                if j in y_k and y_k[k] != j:
                    old_val = y_k[k]
                    y_k[k] = j
                    break

            s = Solution(self.problem, x_jv, y_k, z_j)
            if self.checker.is_feasible(s):
                return s
            else:
                # return solution
                y_k[k] = old_val

        used_vehicles = np.unique(y_k)

        # zamiana wykorzystanych aut
        if np.random.rand() < 0.5 and used_vehicles.size >= 2:
            a = np.random.choice(used_vehicles)
            b = np.random.choice(used_vehicles)
            while a == b:
                b = np.random.choice(used_vehicles)

            y_k[y_k == a], y_k[y_k == b] = b, a
            s = Solution(self.problem, x_jv, y_k, z_j)
            if self.checker.is_feasible(s):
                return s
            else:
                # return solution
                y_k[y_k == a], y_k[y_k == b] = b, a

        # zamiana z niewykorzystanym autem
        if np.random.rand() < 0.5 and used_vehicles.size != self.problem.n_vehicles:
            unused_vehicles = np.setdiff1d(
                np.arange(self.problem.n_vehicles), used_vehicles
            )

            a = np.random.choice(used_vehicles)
            b = np.random.choice(unused_vehicles)

            old_val = z_j[b]
            z_j[b] = z_j[a]
            z_j[a] = -1

            y_k[y_k == a] = b
            s = Solution(self.problem, x_jv, y_k, z_j)
            if self.checker.is_feasible(s):
                return s
            else:
                # return solution
                z_j[a] = z_j[b]
                z_j[b] = old_val
                y_k[y_k == b] = a

        # zmiana trasy
        for j in np.unique(y_k):
            route = solution.get_route(j)
            if route.size > 1 and np.random.rand() < 1:
                a = np.random.randint(route.size) + 1
                b = np.random.randint(route.size) + 1
                while a == b:
                    b = np.random.randint(route.size) + 1

                x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

                s = Solution(self.problem, x_jv, y_k, z_j)
                if self.checker.is_feasible(s):
                    # print(s.get_route(j), self.get_score(s), a, b, route.size)
                    return s
                else:
                    # return solution
                    x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

        return solution

    def run(self, max_iter=1000):
        solutions = self.initial_population
        solutions.sort(key=lambda s: self.get_score(s))
        initial_best = deepcopy(solutions[0])
        l = len(solutions)

        pairs = [(i, j) for i in range(l // 2) for j in range(i + 1, l // 2)]

        def get_pairs():
            index = np.random.randint(low=0, high=len(pairs), size=(l // 2))
            return [pairs[i] for i in index]

        for i in range(max_iter):
            solutions.sort(key=lambda s: self.get_score(s))

            new = [self.crossover(solutions[i], solutions[j]) for i, j in get_pairs()]
            new = [self.mutation(n) for n in new if n]
            o = 1
            while len(new) < l // 2:
                new.append(solutions[l // 2 + o])
                o += 1

            solutions = solutions[: l // 2] + new

            sys.stdout.write("\r" + " " * 80 + "\r" + str(i))
            sys.stdout.flush()

        solutions.sort(key=lambda s: self.get_score(s))
        print()

        # print(self.get_score(best), self.get_score(solutions[0]))
        return initial_best, solutions[0]
