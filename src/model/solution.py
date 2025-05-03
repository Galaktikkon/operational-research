import numpy as np
from .problem import Problem


class Solution:
    def __init__(
        self,
        problem: Problem,
        x_uvj: np.ndarray,
        y_kj: np.ndarray,
        z_ij: np.ndarray,
    ):
        self.problem = problem
        self.x_uvj = x_uvj
        self.z_ij = z_ij
        self.y_kj = y_kj

    def __hash__(self):
        x_hashable = tuple(self.x_uvj.flatten().tolist())
        y_hashable = tuple(self.y_kj.flatten().tolist())
        z_hashable = tuple(self.z_ij.flatten().tolist())

        return hash((x_hashable, y_hashable, z_hashable))

    def __eq__(self, value):
        if not isinstance(value, Solution):
            return False

        return (
            np.all(self.x_uvj == value.x_uvj)
            and np.all(self.y_kj == value.y_kj)
            and np.all(self.z_ij == value.z_ij)
        )

    def __repr__(self):
        rows = []

        for i, j in zip(*self.z_ij.nonzero()):
            courier = self.problem.couriers[i]
            vehicle = self.problem.vehicles[j]

            rows.append(f"{courier} {vehicle}")

            for k in self.y_kj[:, j].nonzero()[0]:
                rows.append(str(self.problem.packages[k]))

            route = [self.problem.graph.warehouse]

            while True:
                v = route[-1]
                next_v = self.x_uvj[v, :, j].argmax()
                if next_v == self.problem.graph.warehouse:
                    break
                v = next_v
                route.append(v)

            rows.append(
                " -> ".join([str(v) for v in route + [self.problem.graph.warehouse]])
            )

            rows.append("")

        return "\n".join(rows)
