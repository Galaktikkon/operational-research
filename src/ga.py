import numpy as np
from model.solution import Solution
from model.problem import Problem


class GA:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.C = 6
        self.alpha = 0.1

    def get_score(self, solution: Solution):
        solution.calc_t_i()
        solution.calc_v_k()
        solution.calc_d_j()

        c_i = np.array([c.hourly_rate for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.t_i @ c_i
        fuel_cost = self.C * (p_j @ solution.d_j)

        delay = self.alpha / self.problem.n_packages * np.sum(solution.v_k - a_k)

        return rates + fuel_cost + delay
