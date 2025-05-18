from .mutation import Mutation
import numpy as np


class PackagesMutation(Mutation):
    def _is_possible(self):
        y_k = self.solution.y_k
        if self.problem.n_packages < 2:
            return False

        for k in np.random.permutation(np.arange(self.problem.n_packages)):
            js = np.unique(y_k)
            js = js[js != y_k[k]]

            if js.size:
                return True

        return False

    def _mutate_solution(self):
        x_jv = self.solution.x_jv
        y_k = self.solution.y_k

        for k in np.random.permutation(np.arange(self.problem.n_packages)):
            js = np.unique(y_k)
            js = js[js != y_k[k]]

            if not js.size:
                continue

            j = np.random.choice(js)
            self.old_j = y_k[k]
            self.old_x = (x_jv[self.old_j].copy(), x_jv[j].copy())
            self.k = k
            self.j = j
            y_k[k] = j
            p = self.problem.packages[k]
            if p.address not in x_jv[j]:
                max_index = np.max(np.where(x_jv[j] != 0)[0]) + 1
                o = np.random.randint(1, max_index)

                for l in range(x_jv[j].size - 1, o, -1):
                    x_jv[j][l] = x_jv[j][l - 1]

                x_jv[j, o] = p.address

            old_j_packages = np.where(y_k == self.old_j)[0]
            old_j_addresses = [self.problem.packages[k].address for k in old_j_packages]

            if p.address not in old_j_addresses:
                o = np.where(x_jv[self.old_j] == p.address)[0][0]

                while x_jv[self.old_j][o] != self.problem.graph.warehouse:
                    x_jv[self.old_j][o] = x_jv[self.old_j][o + 1]
                    o += 1

            return

    def _reverse(self):
        self.solution.y_k[self.k] = self.old_j
        self.solution.x_jv[self.old_j] = self.old_x[0]
        self.solution.x_jv[self.j] = self.old_x[1]
