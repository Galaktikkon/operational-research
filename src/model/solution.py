import numpy as np
from .problem import Problem
from random import sample


class Solution:
    def __init__(
        self,
        problem: Problem,
        x_juv: np.ndarray,
        y_kj: np.ndarray,
        z_ij: np.ndarray,
    ):
        self.problem = problem
        self.x_juv = x_juv
        self.z_ij = z_ij
        self.y_kj = y_kj

        self.t_i: np.ndarray | None = None
        self.v_k: np.ndarray | None = None
        self.d_j: np.ndarray | None = None

    def __hash__(self):
        x_hashable = tuple(self.x_juv.flatten().tolist())
        y_hashable = tuple(self.y_kj.flatten().tolist())
        z_hashable = tuple(self.z_ij.tolist())

        return hash((x_hashable, y_hashable, z_hashable))

    def __eq__(self, value):
        if not isinstance(value, Solution):
            return False

        return (
            np.all(self.x_juv == value.x_juv)
            and np.all(self.y_kj == value.y_kj)
            and np.all(self.z_ij == value.z_ij)
        )

    def __repr__(self):
        rows = []

        for j, i in enumerate(self.z_ij):
            if i == -1:
                continue
            courier = self.problem.couriers[i]
            vehicle = self.problem.vehicles[j]

            rows.append(f"{courier} {vehicle}")

            for k in self.y_kj[:, j].nonzero()[0]:
                rows.append(str(self.problem.packages[k]))

            route = [self.problem.graph.warehouse]

            while True:
                v = route[-1]
                next_v = self.x_juv[j, v].argmax()
                if next_v == self.problem.graph.warehouse:
                    break
                v = next_v
                route.append(v)

            rows.append(
                " -> ".join([str(v) for v in route + [self.problem.graph.warehouse]])
            )

            rows.append("")

        return "\n".join(rows)

    def calc_t_i(self):
        if self.t_i is not None:
            return

        n_nodes = self.problem.graph.n_nodes

        self.t_i = np.zeros(self.problem.n_couriers)
        for i in range(self.problem.n_couriers):
            for j in range(self.problem.n_vehicles):
                s = 0
                for u in range(n_nodes):
                    for v in range(n_nodes):
                        s += self.problem.s_uv[u, v] * self.x_juv[j, u, v]

                z_ij = 1 if self.z_ij[j] == i else 0
                self.t_i[i] += z_ij * s

    def calc_v_k(self):
        if self.v_k is not None:
            return

        n_nodes = self.problem.graph.n_nodes

        self.l_vj = np.zeros((n_nodes, self.problem.n_vehicles))
        for j in range(self.problem.n_vehicles):
            v = self.problem.graph.warehouse

            while True:
                next_v = self.x_juv[j, v].argmax()

                if next_v == self.problem.graph.warehouse:
                    break

                self.l_vj[next_v, j] = self.l_vj[v, j] + self.problem.s_uv[v, next_v]
                v = next_v

        self.v_k = np.zeros(self.problem.n_packages)
        for k in range(self.problem.n_packages):
            p = self.problem.packages[k]
            for j in range(self.problem.n_vehicles):
                self.v_k[k] += self.y_kj[k, j] * self.l_vj[p.address, j]

    def calc_d_j(self):
        if self.d_j is not None:
            return

        self.d_j = np.zeros(self.problem.n_vehicles)
        for j in range(self.problem.n_vehicles):
            self.d_j[j] = np.sum(self.x_juv[j] * self.problem.g_uv)

    def swap_random_pair(self, list_):
        indices = [i for i in range(len(list_))]
        first, second = sample(indices, 2)
        list_[first], list_[second] = list_[second], list_[first]

    def __invert__(self):
        self.swap_random_pair(self.z_ij)
        self.swap_random_pair(self.y_kj)
