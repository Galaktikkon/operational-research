import numpy as np

from model.problem import Problem
from model.solution import Solution


class SolutionChecker:
    """Class to check the feasibility of a solution for the problem.

    Args
    ----
        problem (Problem): The problem to check solutions for.

    Methods
    -------
        is_feasible(solution: Solution, debug: bool = False) -> bool: Check if the given solution is feasible for the problem.
    """

    def __init__(self, problem: Problem):
        self.problem = problem
        self.solution: Solution | None = None

    def is_feasible(self, solution: Solution, debug=False):
        """Check if the given solution is feasible for the problem. It uses subsequent checks
        to verify the solution's validity. The checks are based on the problem's constraints.

        Args
        ----
            solution (Solution): The solution to check.
            debug (bool): If True, print debug information.

        Returns
        -------
            bool: True if the solution is feasible, False otherwise.
        """
        self.solution = solution

        func_names = sorted(
            [key for key in dir(self) if "_SolutionChecker__check" in key]
        )
        funcs = [getattr(self, key) for key in func_names]

        for func, name in zip(funcs, func_names):
            if not func():
                if debug:
                    print(f"\nerror in {name}")
                return False

        self.solution = None
        return True

    def __check_1(self):
        """ """
        non_empty = self.solution.z_j != -1
        return np.unique(self.solution.z_j[non_empty]).size == non_empty.sum()

    def __check_4(self):
        """
        Check if each courier's work limit is respected.
        """
        b_i = np.array([c.work_limit for c in self.problem.couriers])
        return np.all(self.solution.get_t_i() <= b_i)

    def __check_5(self):
        """
        Check if each courier has a permission for the vehicle they are assigned to.
        """
        r_j = np.zeros_like(self.solution.z_j)

        for courier, vehicle in self.problem.permissions:
            r_j[vehicle] = courier

        # may ride or not ride the vehicle the courier is assigned to
        return np.all(self.solution.z_j <= r_j)

    def __check_6(self):
        """
        Check if each package is delivered to its destination
        """
        for k, p in enumerate(self.problem.packages):
            j = self.solution.y_k[k]
            if p.address not in self.solution.x_jv[j]:
                return False

        return True

    def __check_7(self):
        """
        Check if the pickup/delivery time is in the allowed time window.
        """
        a = np.array([p.start_time for p in self.problem.packages])
        b = np.array([p.end_time for p in self.problem.packages])

        return np.all((a <= self.solution.get_v_k()) & (self.solution.get_v_k() <= b))

    def __check_9(self):
        """
        Check if the vehicle routes are continuous and start/end at the warehouse.
        """
        for j in range(self.problem.n_vehicles):
            route = self.solution.x_jv[j]
            last = self.problem.n_nodes

            non_zero = np.where(route != 0)[0]
            if len(non_zero) >= 1:
                diffs = np.diff(non_zero)
                if not np.all(diffs == 1) or non_zero[0] != 1 or non_zero[-1] == last:
                    return False

        return True

    def __check_11(self):
        """
        Check if the vehicle capacity is respected.
        """
        for j, veh in enumerate(self.problem.vehicles):
            for v in range(self.problem.n_nodes):
                if self.solution.get_m_jv()[j, v] > veh.capacity:
                    return False
        return True
