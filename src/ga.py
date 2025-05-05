import numpy as np
from model.solution import Solution
from model.problem import Problem
from solution_checker import SolutionChecker
import functools
from copy import deepcopy
from ui.draw_solution import draw_solution


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
                return solution
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
                return solution
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
                return solution
                z_j[a] = z_j[b]
                z_j[b] = old_val
                y_k[y_k == b] = a

        # zmiana trasy
        for j in np.unique(y_k):
            route = solution.get_route(j)
            if route.size > 1 and np.random.rand() < 0.9:
                a = np.random.randint(route.size) + 1
                b = np.random.randint(route.size) + 1
                while a == b:
                    b = np.random.randint(route.size) + 1

                x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

                s = Solution(self.problem, x_jv, y_k, z_j)

                s = Solution(self.problem, x_jv, y_k, z_j)
                if self.checker.is_feasible(s):
                    # print("udana zamiana")
                    # draw_solution(s)
                    return s
                else:
                    return solution
                    x_jv[j, a], x_jv[j, b] = x_jv[j, b], x_jv[j, a]

        return solution

    def run(self):
        solutions = self.initial_population
        solutions.sort(key=lambda s: self.get_score(s))
        best = deepcopy(solutions[0])

        for i in range(10000):
            solutions = solutions + [self.mutation(s) for s in solutions]
            solutions.sort(key=lambda s: self.get_score(s))
            solutions = solutions[:8]
            # print(self.get_score(solutions[0]))
            # ok = solutions[: len(solutions) // 2]
            # # # bad = solutions[10:]

            # solutions = ok + [self.mutation(s) for s in ok]
            # # solutions.sort(key=lambda s: self.get_score(s))
            if i % 100 == 0:
                print(i)

        print(self.get_score(best), self.get_score(solutions[0]))
        return best, solutions[0]
