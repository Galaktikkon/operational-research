import numpy as np
from model.solution import Solution
from model.problem import Problem


class SolutionChecker:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.solution: Solution | None = None

    def is_feasible(self, solution: Solution):
        self.solution = solution

        func_names = sorted(
            [key for key in dir(self) if "_SolutionChecker__check" in key]
        )
        funcs = [getattr(self, key) for key in func_names]

        for func, name in zip(funcs, func_names):
            if not func():
                # print(f"\nerror in {name}")
                return False

        self.solution = None
        return True

    def __check_1(self):
        non_empty = self.solution.z_j != -1
        return np.unique(self.solution.z_j[non_empty]).size == non_empty.sum()

    def __check_4(self):
        b_i = np.array([c.work_limit for c in self.problem.couriers])
        return np.all(self.solution.get_t_i() <= b_i)

    def __check_5(self):
        r_j = np.zeros_like(self.solution.z_j)

        for courier, vehicle in self.problem.permissions:
            r_j[vehicle] = courier

        return np.all(self.solution.z_j <= r_j)

    def __check_6(self):
        for k, p in enumerate(self.problem.packages):
            j = self.solution.y_k[k]
            if p.address not in self.solution.x_jv[j]:
                return False

        return True

    def __check_7(self):
        a = np.array([p.start_time for p in self.problem.packages])
        b = np.array([p.end_time for p in self.problem.packages])

        return np.all((a <= self.solution.get_v_k()) & (self.solution.get_v_k() <= b))

    def __check_9(self):
        for j in range(self.problem.n_vehicles):
            route = self.solution.x_jv[j]
            last = self.problem.n_nodes - 1

            non_zero = np.where(route != 0)[0]
            if len(non_zero) >= 1:
                diffs = np.diff(non_zero)
                if not np.all(diffs == 1) or non_zero[0] != 1 or non_zero[-1] == last:
                    return False

        return True

    def __check_11(self):
        for j, veh in enumerate(self.problem.vehicles):
            l_v = np.zeros((self.problem.graph.n_nodes))
            s = 0
            for k, p in enumerate(self.problem.packages):
                if p.type == "delivery" and self.solution.y_k[k] == j:
                    s += p.weight

            if s > veh.capacity:
                return False

            l_v[self.problem.graph.warehouse] = s

            for v, next_v in zip(self.solution.x_jv[j], self.solution.x_jv[j, 1:]):
                if next_v == self.problem.graph.warehouse:
                    break

                delivery = 0
                for k, p in enumerate(self.problem.packages):
                    if (
                        p.type == "delivery"
                        and p.address == next_v
                        and self.solution.y_k[k] == j
                    ):
                        delivery += p.weight

                pickup = 0
                for k, p in enumerate(self.problem.packages):
                    if (
                        p.type == "pickup"
                        and p.address == next_v
                        and self.solution.y_k[k] == j
                    ):
                        pickup += p.weight

                l_v[next_v] = l_v[v] - delivery + pickup

                if l_v[next_v] > veh.capacity:
                    return False

        return True
