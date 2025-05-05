import numpy as np
from model.solution import Solution
from model.problem import Problem
from solution_checker import SolutionChecker


class GA:
    def __init__(self, problem: Problem, initial_population: list[Solution]):
        self.problem = problem
        self.checker = SolutionChecker(problem)
        self.C = 6
        self.alpha = 0.1
        self.initial_population = initial_population

    def get_score(self, solution: Solution):
        c_i = np.array([c.hourly_rate for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.get_t_i() @ c_i
        fuel_cost = self.C * (p_j @ solution.get_d_j())

        delay = self.alpha / self.problem.n_packages * np.sum(solution.get_v_k() - a_k)

        return rates + fuel_cost + delay
