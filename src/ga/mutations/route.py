import numpy as np

from model import Solution

from .mutation import Mutation


class RouteMutation(Mutation):
    def __init__(self, solution: Solution, j):
        super().__init__(solution)
        self.j = j
        self.route = solution.get_route(j)

    def _is_possible(self):
        return self.route.size > 1

    def _mutate_solution(self):
        route = self.route
        x_jv = self.solution.x_jv
        j = self.j

        self.a = np.random.randint(route.size) + 1
        self.b = np.random.randint(route.size) + 1
        while self.a == self.b:
            self.b = np.random.randint(route.size) + 1

        x_jv[j, self.a], x_jv[j, self.b] = x_jv[j, self.b], x_jv[j, self.a]

    def _reverse(self):
        x_jv = self.solution.x_jv
        j = self.j
        x_jv[j, self.a], x_jv[j, self.b] = x_jv[j, self.b], x_jv[j, self.a]
