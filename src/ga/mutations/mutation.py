import numpy as np

from model import Solution


class Mutation:
    proba = 0.5
    times_feasible_created = 0
    times_run = 0

    def __init__(self, solution: Solution):
        self.solution = solution
        self.problem = solution.problem

    def is_possible(self) -> bool:
        p = np.random.rand() < self.proba
        if hasattr(self, "_is_possible"):
            return p and self._is_possible()
        return p

    def mutate_solution(self):
        self._mutate_solution()
        self.__class__.times_feasible_created += 1
        self.__class__.times_run += 1
        self.solution.recalculate()

    def reverse(self):
        self._reverse()
        self.__class__.times_feasible_created -= 1
        self.solution.recalculate()

    def _reverse(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def _mutate_solution(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def _is_possible(self):
        raise NotImplementedError("Subclasses should implement this method.")
