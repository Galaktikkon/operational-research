from .mutation import Mutation
import numpy as np


class CouriersMutation(Mutation):
    def _is_possible(self):
        return self.problem.n_couriers >= 2

    def _mutate_solution(self):
        z_j = self.solution.z_j

        self.i1 = np.random.randint(self.problem.n_couriers)
        self.i2 = np.random.randint(self.problem.n_couriers)
        while self.problem.n_couriers > 1 and self.i1 == self.i2:
            self.i2 = np.random.randint(self.problem.n_couriers)

        j1 = np.where(z_j == self.i1)[0]
        self.j1 = j1[0] if j1.size else None

        j2 = np.where(z_j == self.i2)[0]
        self.j2 = j2[0] if j2.size else None

        if j1 is not None:
            z_j[j1] = self.i2
        if j2 is not None:
            z_j[j2] = self.i1

    def _reverse(self):
        if self.j1 is not None:
            self.solution.z_j[self.j1] = self.i1
        if self.j2 is not None:
            self.solution.z_j[self.j2] = self.i2
