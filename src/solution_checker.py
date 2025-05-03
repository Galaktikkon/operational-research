import numpy as np
from model.solution import Solution
from model.problem import Problem


class SolutionChecker:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.solution: Solution | None = None

    def prepare_check(self):
        n_nodes = self.problem.graph.n_nodes

        self.s_uv = np.zeros((n_nodes, n_nodes))
        self.g_uv = np.zeros((n_nodes, n_nodes))

        for u, v, dist, time in self.problem.graph.routes:
            self.s_uv[u, v] = dist
            self.g_uv[u, v] = time

        self.t_i = np.zeros(self.problem.n_couriers)
        for i in range(self.problem.n_couriers):
            for j in range(self.problem.n_vehicles):
                s = 0
                for u in range(n_nodes):
                    for v in range(n_nodes):
                        s += self.s_uv[u, v] * self.solution.x_uvj[u, v, j]

                self.t_i[i] += self.solution.z_ij[i, j] * s

        self.l_vj = np.zeros((n_nodes, self.problem.n_vehicles))
        for j in range(self.problem.n_vehicles):
            v = self.problem.graph.warehouse

            while True:
                next_v = self.solution.x_uvj[v, :, j].argmax()

                if next_v == self.problem.graph.warehouse:
                    break

                self.l_vj[next_v, j] = self.l_vj[v, j] + self.s_uv[v, next_v]
                v = next_v

        self.v_k = np.zeros(self.problem.n_packages)
        for k in range(self.problem.n_packages):
            p = self.problem.packages[k]
            for j in range(self.problem.n_vehicles):
                self.v_k[k] += self.solution.y_kj[k, j] * self.l_vj[p.address, j]

    def is_feasible(self, solution: Solution):
        self.solution = solution
        self.prepare_check()

        func_names = [key for key in dir(self) if "_SolutionChecker__check" in key]
        funcs = [getattr(self, key) for key in func_names]

        for func, name in zip(funcs, func_names):
            if not func():
                # print(f"error in {name}")
                return False

        self.solution = None
        return True

    def __check_1(self):
        return np.all(self.solution.z_ij.sum(axis=1) <= 1)

    def __check_2(self):
        return np.all(self.solution.z_ij.sum(axis=0) <= 1)

    def __check_3(self):
        return np.all(self.solution.y_kj.sum(axis=1) == 1)

    def __check_4(self):
        b_i = np.array([c.work_limit for c in self.problem.couriers])
        return np.all(self.t_i <= b_i)

    def __check_5(self):
        r_ij = np.zeros_like(self.solution.z_ij)

        for courier, vehicle in self.problem.permissions:
            r_ij[courier, vehicle] = 1

        return np.all(self.solution.z_ij <= r_ij)

    def __check_6(self):
        for k, p in enumerate(self.problem.packages):
            for j in range(self.problem.n_vehicles):
                s = 0
                for u in range(self.problem.graph.n_nodes):
                    s += self.solution.x_uvj[u, p.address, j]

                if not self.solution.y_kj[k, j] <= s:
                    return False

        return True

    def __check_7(self):
        a = np.array([p.start_time for p in self.problem.packages])
        b = np.array([p.end_time for p in self.problem.packages])

        return np.all(a <= self.v_k <= b)

    def __check_8(self):
        for j in range(self.problem.n_vehicles):
            s = 0

            for v in range(self.problem.graph.n_nodes):
                if v != self.problem.graph.warehouse:
                    s += self.solution.x_uvj[self.problem.graph.warehouse, v, j]

            if s > 1:
                return False

        return True

    def __check_9(self):
        for j in range(self.problem.n_vehicles):
            s1 = 0
            s2 = 0

            for v in range(self.problem.graph.n_nodes):
                if v != self.problem.graph.warehouse:
                    s1 += self.solution.x_uvj[self.problem.graph.warehouse, v, j]
                    s2 += self.solution.x_uvj[v, self.problem.graph.warehouse, j]

            if s1 != s2:
                return False

        return True

    def __check_10(self):
        for j in range(self.problem.n_vehicles):
            for v in range(self.problem.graph.n_nodes):
                if v != self.problem.graph.warehouse:
                    s1 = 0
                    s2 = 0
                    for u in range(self.problem.graph.n_nodes):
                        s1 += self.solution.x_uvj[u, v, j]
                        s2 += self.solution.x_uvj[v, u, j]

                    if s1 != s2:
                        return False

        return True

    def __check_11(self):
        for j, veh in enumerate(self.problem.vehicles):
            l_v = np.zeros((self.problem.graph.n_nodes))
            s = 0
            for k, p in enumerate(self.problem.packages):
                if p.type == "delivery":
                    s += self.solution.y_kj[k, j] * p.weight

            if s > veh.capacity:
                return False

            l_v[self.problem.graph.warehouse] = s

            v = self.problem.graph.warehouse

            while True:
                next_v = self.solution.x_uvj[v, :, j].argmax()

                if next_v == self.problem.graph.warehouse:
                    break

                delivery = 0
                for k in range(self.problem.n_packages):
                    p = self.problem.packages[k]
                    if (
                        p.type == "delivery"
                        and p.address == next_v
                        and self.solution.y_kj[k, j]
                    ):
                        delivery += p.weight

                pickup = 0
                for k in range(self.problem.n_packages):
                    p = self.problem.packages[k]
                    if (
                        p.type == "pickup"
                        and p.address == next_v
                        and self.solution.y_kj[k, j]
                    ):
                        pickup += p.weight

                l_v[next_v] = l_v[v] - delivery + pickup

                if l_v[next_v] > veh.capacity:
                    return False

                v = next_v

        return True
