import numpy as np

from .mutation import Mutation


class UsedVehiclesMutation(Mutation):
    def __init__(self, solution):
        super().__init__(solution)
        self.used_vehicles = np.unique(self.solution.y_k)

    def _is_possible(self):
        return self.used_vehicles.size >= 2

    def _mutate_solution(self):
        x_jv = self.solution.x_jv
        y_k = self.solution.y_k
        used_vehicles = self.used_vehicles

        self.a = np.random.choice(used_vehicles)
        self.b = np.random.choice(used_vehicles)
        while self.a == self.b:
            self.b = np.random.choice(used_vehicles)

        self.old_y_k = y_k.copy()
        self.old_x = (x_jv[self.a].copy(), x_jv[self.b].copy())

        xd = x_jv[self.b].copy()
        x_jv[self.b] = x_jv[self.a]
        x_jv[self.a] = xd

        y_k[self.old_y_k == self.a] = self.b
        y_k[self.old_y_k == self.b] = self.a

    def _reverse(self):
        self.solution.y_k = self.old_y_k
        self.solution.x_jv[self.a] = self.old_x[0]
        self.solution.x_jv[self.b] = self.old_x[1]


class UnusedVehiclesMutation(Mutation):
    def __init__(self, solution):
        super().__init__(solution)
        self.used_vehicles = np.unique(self.solution.y_k)

    def _is_possible(self):
        return self.used_vehicles.size != self.problem.n_vehicles

    def _mutate_solution(self):
        used_vehicles = self.used_vehicles
        x_jv = self.solution.x_jv
        y_k = self.solution.y_k
        z_j = self.solution.z_j

        unused_vehicles = np.setdiff1d(
            np.arange(self.problem.n_vehicles), used_vehicles
        )

        self.a = np.random.choice(used_vehicles)
        self.b = np.random.choice(unused_vehicles)

        self.old_z = z_j[self.b]
        z_j[self.b] = z_j[self.a]
        z_j[self.a] = -1

        self.old_y = y_k.copy()
        y_k[y_k == self.a] = self.b

        self.old_x = x_jv[self.a].copy()
        x_jv[self.b] = x_jv[self.a].copy()
        x_jv[self.a] = np.full_like(x_jv[self.a], self.solution.problem.graph.warehouse)

    def _reverse(self):
        x_jv = self.solution.x_jv
        z_j = self.solution.z_j

        x_jv[self.b] = np.full_like(x_jv[self.a], self.solution.problem.graph.warehouse)
        x_jv[self.a] = self.old_x

        self.solution.y_k = self.old_y

        z_j[self.a] = z_j[self.b]
        z_j[self.b] = self.old_z
