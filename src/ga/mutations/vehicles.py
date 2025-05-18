from .mutation import Mutation
import numpy as np


class UsedVehiclesMutation(Mutation):
    def __init__(self, solution):
        super().__init__(solution)
        self.used_vehicles = np.unique(self.solution.y_k)

    def _is_possible(self):
        return self.used_vehicles.size >= 2

    def _mutate_solution(self):
        y_k = self.solution.y_k
        used_vehicles = self.used_vehicles

        self.a = np.random.choice(used_vehicles)
        self.b = np.random.choice(used_vehicles)
        while self.a == self.b:
            self.b = np.random.choice(used_vehicles)

        y_k[y_k == self.a], y_k[y_k == self.b] = self.b, self.a

    def _reverse(self):
        y_k = self.solution.y_k
        y_k[y_k == self.a], y_k[y_k == self.b] = self.b, self.a


class UnusedVehiclesMutation(Mutation):
    def __init__(self, solution):
        super().__init__(solution)
        self.used_vehicles = np.unique(self.solution.y_k)

    def _is_possible(self):
        return self.used_vehicles.size != self.problem.n_vehicles

    def _mutate_solution(self):
        used_vehicles = self.used_vehicles
        y_k = self.solution.y_k
        z_j = self.solution.z_j

        unused_vehicles = np.setdiff1d(
            np.arange(self.problem.n_vehicles), used_vehicles
        )

        self.a = np.random.choice(used_vehicles)
        self.b = np.random.choice(unused_vehicles)

        self.old_val = z_j[self.b]
        z_j[self.b] = z_j[self.a]
        z_j[self.a] = -1

        y_k[y_k == self.a] = self.b

    def _reverse(self):
        y_k = self.solution.y_k
        z_j = self.solution.z_j
        z_j[self.a] = z_j[self.b]
        z_j[self.b] = self.old_val
        y_k[y_k == self.b] = self.a
