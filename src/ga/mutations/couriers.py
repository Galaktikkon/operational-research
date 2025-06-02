import numpy as np

from .mutation import Mutation


class CouriersMutation(Mutation):
    def _is_possible(self):
        """
        Check if the mutation is possible.
        This mutation is possible if there are at least two couriers available.

        Returns:
            bool: True if the mutation can be applied, False otherwise.
        """
        return self.problem.n_couriers >= 2

    def _mutate_solution(self):
        """
        Swap the couriers of two drivers.
        This mutation randomly selects two drivers and swaps their assigned couriers.
        It ensures that the two selected drivers are not the same and that the
        selected drivers have at least one courier assigned to them.
        """
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
        """
        Reverse the mutation by swapping the couriers back to their original drivers.
        This method restores the original assignments of couriers to drivers
        after the mutation has been applied.
        """
        self.solution.z_j[self.j1] = self.i1
        if self.j2 is not None:
            self.solution.z_j[self.j2] = self.i2
