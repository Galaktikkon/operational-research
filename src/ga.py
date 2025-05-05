import numpy as np
from model.solution import Solution
from model.problem import Problem
from solution_checker import SolutionChecker
import functools


class GA:
    def __init__(self, problem: Problem, initial_population: list[Solution]):
        self.problem = problem
        self.checker = SolutionChecker(problem)
        self.C = 6
        self.alpha = 0.1
        self.initial_population = initial_population

    @functools.cache
    def get_score(self, solution: Solution):
        c_i = np.array([c.hourly_rate for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.get_t_i() @ c_i
        fuel_cost = self.C * (p_j @ solution.get_d_j())

        delay = self.alpha / self.problem.n_packages * np.sum(solution.get_v_k() - a_k)

        return rates + fuel_cost + delay

    def crossover(self, s1: Solution, s2: Solution): ...

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

            # s = Solution(self.problem, x_jv, y_k, z_j)
            # if not self.checker.is_feasible(s):
            #     if j1 is not None:
            #         z_j[j1] = i1
            #     if j2 is not None:
            #         z_j[j2] = i2

        # przeniesienie paczki
        if np.random.rand() < 0.5:
            ...
        # zamiana aut
        if np.random.rand() < 0.5:
            ...

        # zmiana trasy
        for j in range(self.problem.n_vehicles):
            route = solution.get_route(j)
            if route.size > 1 and np.random.rand() < 0.5:
                a = np.random.randint(route.size) + 1
                b = np.random.randint(route.size) + 1
                while a == b:
                    b = np.random.randint(route.size) + 1

                x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

                # s = Solution(self.problem, x_jv, y_k, z_j)
                # if not self.checker.is_feasible(s):
                #     x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

        s = Solution(self.problem, x_jv, y_k, z_j)
        if not self.checker.is_feasible(s):
            return solution

        return s

    def run(self):
        solutions = self.initial_population
        solutions.sort(key=lambda s: self.get_score(s))
        best = self.get_score(solutions[0])

        for i in range(1000):
            ok = solutions  # [:30]
            bad = solutions  # [30:60]

            solutions = solutions + [self.mutation(s) for s in solutions]
            solutions.sort(key=lambda s: self.get_score(s))
            if i % 100 == 0:
                print(i)

        print(best, self.get_score(solutions[0]))
        return solutions[0]
