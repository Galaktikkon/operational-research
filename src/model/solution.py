import numpy as np
from .problem import Problem
from itertools import dropwhile, accumulate


def trim_trailing(lst, val):
    return list(reversed(list(dropwhile(lambda x: x == val, reversed(lst)))))


class Solution:
    def __init__(
        self,
        problem: Problem,
        x_jv: np.ndarray,
        y_k: np.ndarray,
        z_j: np.ndarray,
    ):
        self.problem = problem
        self.x_jv = x_jv
        self.z_j = z_j
        self.y_k = y_k

        self._t_i: np.ndarray | None = None
        self._v_k: np.ndarray | None = None
        self._d_j: np.ndarray | None = None
        self._l_vj: np.ndarray | None = None
        self._m_jv: np.ndarray | None = None

    def recalculate(self):
        self._t_i = None
        self._v_k = None
        self._d_j = None
        self._l_vj = None
        self._m_jv = None

    def __hash__(self):
        x_hashable = tuple(self.x_jv.flatten().tolist())
        y_hashable = tuple(self.y_k.tolist())
        z_hashable = tuple(self.z_j.tolist())

        return hash((x_hashable, y_hashable, z_hashable))

    def __eq__(self, value):
        if not isinstance(value, Solution):
            return False

        return (
            np.all(self.x_jv == value.x_jv)
            and np.all(self.y_k == value.y_k)
            and np.all(self.z_j == value.z_j)
        )

    def __repr__(self):
        rows = []

        for j, i in enumerate(self.z_j):
            if i == -1:
                continue
            courier = self.problem.couriers[i]
            vehicle = self.problem.vehicles[j]

            rows.append(f"{courier} {vehicle}")

            for k in np.where(self.y_k == j)[0]:
                rows.append(str(self.problem.packages[k]))

            route = self.get_route(j, True, True)

            rows.append("  ->  ".join([f"{v:5}" for v in route]))

            time = [0] + [self.get_l_vj()[v, j] for v in route[1:]]
            capacity = [self.get_m_jv()[j, v] for v in route[:-1]] + [0]

            time = [f"{t:5.2f}" for t in time]
            capacity = [f"{c:5.2f}" for c in capacity]

            route_pairs = [p for p in zip(route, route[1:])]

            dist = [0] + [self.problem.graph.dist[u, v] for u, v in route_pairs]
            dist = list(accumulate(dist))
            dist = [f"{d:5.2f}" for d in dist]

            rows.append("      ".join(time) + " [min]")
            rows.append("      ".join(dist) + " [km]")
            rows.append("      ".join(capacity) + " [kg]")

            rows.append("")

        return "\n".join(rows)

    def get_route(self, j, leading_warehouse=False, trailing_warehouse=False):
        warehouse = self.problem.graph.warehouse
        route = self.x_jv[j][self.x_jv[j] != warehouse]

        if leading_warehouse:
            route = np.insert(route, 0, warehouse)

        if trailing_warehouse:
            route = np.append(route, warehouse)

        return route

    def get_t_i(self):
        if self._t_i is not None:
            return self._t_i

        warehouse = self.problem.graph.warehouse

        self._t_i = np.zeros(self.problem.n_couriers)
        for i in range(self.problem.n_couriers):
            j = np.where(self.z_j == i)[0]
            if j.size:
                j = j[0]
                self._t_i[i] = self.get_l_vj()[warehouse, j]

        return self._t_i

    def get_l_vj(self):
        if self._l_vj is not None:
            return self._l_vj

        n_nodes = self.problem.graph.n_nodes

        self._l_vj = np.zeros((n_nodes, self.problem.n_vehicles))
        for j in range(self.problem.n_vehicles):
            for u, v in zip(self.x_jv[j], self.x_jv[j, 1:]):
                self._l_vj[v, j] = self._l_vj[u, j] + self.problem.s_uv[u, v]
                if v == self.problem.graph.warehouse:
                    break

        return self._l_vj

    def get_v_k(self):
        if self._v_k is not None:
            return self._v_k

        self._v_k = np.zeros(self.problem.n_packages)
        for k, p in enumerate(self.problem.packages):
            for j in range(self.problem.n_vehicles):
                if self.y_k[k] == j:
                    self._v_k[k] += self.get_l_vj()[p.address, j]

        return self._v_k

    def get_d_j(self):
        if self._d_j is not None:
            return self._d_j

        self._d_j = np.zeros(self.problem.n_vehicles)
        for j in range(self.problem.n_vehicles):
            for u, v in zip(self.x_jv[j], self.x_jv[j, 1:]):
                self._d_j[j] += self.problem.g_uv[u, v]
                if v == self.problem.graph.warehouse:
                    break

        return self._d_j

    def get_m_jv(self):
        if self._m_jv is not None:
            return self._m_jv

        self._m_jv = np.zeros((self.problem.n_vehicles, self.problem.graph.n_nodes))
        for j in range(self.problem.n_vehicles):
            s = 0
            for k, p in enumerate(self.problem.packages):
                if p.type == "delivery" and self.y_k[k] == j:
                    s += p.weight

            self._m_jv[j, self.problem.graph.warehouse] = s

            for v, next_v in zip(self.x_jv[j], self.x_jv[j, 1:]):
                if next_v == self.problem.graph.warehouse:
                    break

                delivery = 0
                for k, p in enumerate(self.problem.packages):
                    if (
                        p.type == "delivery"
                        and p.address == next_v
                        and self.y_k[k] == j
                    ):
                        delivery += p.weight

                pickup = 0
                for k, p in enumerate(self.problem.packages):
                    if p.type == "pickup" and p.address == next_v and self.y_k[k] == j:
                        pickup += p.weight

                self._m_jv[j, next_v] = self._m_jv[j, v] - delivery + pickup

        return self._m_jv
