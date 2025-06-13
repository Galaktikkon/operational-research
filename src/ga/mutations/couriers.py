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


class NewCourierMutation(Mutation):
    def _is_possible(self):
        problem = self.problem
        z_j = self.solution.z_j

        used_couriers = np.unique(z_j)
        self.used_couriers = used_couriers[used_couriers != -1]
        self.unused_couriers = np.setdiff1d(
            np.arange(problem.n_couriers), self.used_couriers, assume_unique=True
        )

        self.used_vehicles = np.unique(self.solution.y_k)
        self.unused_vehicles = np.setdiff1d(
            np.arange(self.problem.n_vehicles), self.used_vehicles
        )
        for _ in range(2 * self.unused_couriers.size):
            self.i = np.random.choice(self.unused_couriers)

            courier_vehicles = np.unique(
                [
                    p[1]
                    for p in self.problem.permissions
                    if p[0] == self.i and p[1] in self.unused_vehicles
                ]
            )

            if courier_vehicles.size:
                self.j = np.random.choice(courier_vehicles)
                return True

        return False

    def _mutate_solution(self):
        new_i = self.i
        new_j = self.j
        y_k = self.solution.y_k

        self.old_x_jv = self.solution.x_jv.copy()
        self.old_y_k = self.solution.y_k.copy()

        moved_packages = []
        moved_capacity = 0
        wh = self.problem.graph.warehouse

        def calc_time(new_address):
            route = (
                [wh]
                + np.unique([p.address for p, _ in moved_packages]).tolist()
                + [new_address, wh]
            )
            return sum([self.problem.s_uv[u, v] for u, v in zip(route, route[1:])])

        for k in np.random.permutation(np.arange(self.problem.n_packages)):
            j = y_k[k]
            proba = np.sum(y_k == j) / y_k.size
            p = self.problem.packages[k]

            if (
                np.random.rand() < proba
                and calc_time(p.address) <= self.problem.couriers[new_i].work_limit
                and moved_capacity + p.weight <= self.problem.vehicles[new_j].capacity
            ):
                moved_packages.append((p, k))
                moved_capacity += p.weight

        self.moved_packages = moved_packages
        self.__move_packages()

    def __move_packages(self):
        x_jv = self.solution.x_jv
        y_k = self.solution.y_k
        new_i = self.i
        new_j = self.j
        wh = self.problem.graph.warehouse

        self.solution.z_j[new_j] = new_i

        affected_vehicles = np.unique([y_k[k] for _, k in self.moved_packages])

        x_jv[new_j] = np.full_like(x_jv[new_j], wh)

        for _, k in self.moved_packages:
            y_k[k] = new_j

        for b, v in enumerate(
            np.unique([p.address for p, _ in self.moved_packages]), start=1
        ):
            x_jv[new_j, b] = v

        for old_j in affected_vehicles:
            old_j_packages = np.where(y_k == old_j)[0]
            old_j_addresses = [self.problem.packages[k].address for k in old_j_packages]

            if not len(old_j_addresses):
                self.solution.z_j[old_j] = -1

            for address in self.solution.get_route(old_j):
                if address not in old_j_addresses:
                    o = np.where(x_jv[old_j] == address)[0][0]

                    while x_jv[old_j][o] != self.problem.graph.warehouse:
                        x_jv[old_j][o] = x_jv[old_j][o + 1]
                        o += 1

    def _reverse(self):
        """
        Reverse the mutation by swapping the couriers back to their original drivers.
        This method restores the original assignments of couriers to drivers
        after the mutation has been applied.
        """
        self.solution.z_j[self.j] = -1
        self.solution.x_jv = self.old_x_jv
        self.solution.y_k = self.old_y_k
