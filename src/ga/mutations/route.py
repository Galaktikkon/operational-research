import numpy as np

from model import Solution

from .mutation import Mutation


class RouteMutation(Mutation):
    def __init__(self, solution: Solution, j):
        super().__init__(solution)
        self.j = j
        self.route = solution.get_route(j)

    def _is_possible(self):
        """Check if the mutation is possible.
        This mutation is possible if the route of the vehicle has more than one address.

        Returns:
            bool: True if the mutation can be applied, False otherwise.
        """
        return self.route.size > 1

    def _mutate_solution(self):
        """Swap two addresses in the route of a specific vehicle.
        This mutation randomly selects two different addresses in the route of a vehicle
        and swaps their positions.
        """
        route = self.route
        x_jv = self.solution.x_jv
        j = self.j

        self.a = np.random.randint(route.size) + 1
        self.b = np.random.randint(route.size) + 1
        while self.a == self.b:
            self.b = np.random.randint(route.size) + 1

        x_jv[j, self.a], x_jv[j, self.b] = x_jv[j, self.b], x_jv[j, self.a]

    def _reverse(self):
        """Reverse the swap of two addresses in the route of a specific vehicle.
        This method restores the original positions of the two addresses that were swapped
        during the mutation.
        """
        x_jv = self.solution.x_jv
        j = self.j
        x_jv[j, self.a], x_jv[j, self.b] = x_jv[j, self.b], x_jv[j, self.a]
