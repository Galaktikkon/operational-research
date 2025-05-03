import numpy as np


class Solution:
    def __init__(
        self,
        x_uvj: np.ndarray,
        y_kj: np.ndarray,
        z_ij: np.ndarray,
    ):
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
