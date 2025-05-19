import numpy as np

from .mutation import Mutation


class CouriersMutation(Mutation):
    def _is_possible(self):
        return self.problem.n_couriers >= 2

    def _mutate_solution(self):
        z_j = self.solution.z_j

        drivers = np.unique(z_j)
        drivers = drivers[drivers != -1]

        self.i1 = np.random.choice(drivers)
        self.i2 = np.random.randint(self.problem.n_couriers)
        while self.i1 == self.i2:
            self.i2 = np.random.randint(self.problem.n_couriers)

        self.j1 = np.where(z_j == self.i1)[0][0]

        j2 = np.where(z_j == self.i2)[0]
        self.j2 = j2[0] if j2.size else None

        z_j[self.j1] = self.i2
        if j2 is not None:
            z_j[j2] = self.i1

    def _reverse(self):
        self.solution.z_j[self.j1] = self.i1
        if self.j2 is not None:
            self.solution.z_j[self.j2] = self.i2
