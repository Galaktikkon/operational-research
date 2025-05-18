from .mutation import Mutation
import numpy as np


class PackagesMutation(Mutation):
    def _is_possible(self):
        return self.problem.n_packages >= 2

    def _mutate_solution(self):
        y_k = self.solution.y_k

        k = np.random.randint(self.problem.n_packages)
        for _ in range(100):
            j = np.random.randint(self.problem.n_vehicles)
            if j in y_k and y_k[k] != j:
                self.old_val = y_k[k]
                self.k = k
                y_k[k] = j
                return

    def _reverse(self):
        self.solution.y_k[self.k] = self.old_val
