import numpy as np

from model import Solution


class Mutation:
    """Base class for mutations in a genetic algorithm.
    This class defines the interface for mutations that can be applied to a solution.
    It includes methods to check if a mutation is possible, mutate the solution,
    reverse the mutation, and track the number of feasible solutions created.

    Attributes:
        proba (float): Probability of applying the mutation.
        times_feasible_created (int): Counter for the number of feasible solutions created.
        times_run (int): Counter for the number of times the mutation has been run.
        solution (Solution): The solution to be mutated.
        problem: The problem associated with the solution.

    Methods:
        is_possible() -> bool:
            Checks if the mutation can be applied to the solution.
        mutate_solution():
            Applies the mutation to the solution.
        reverse():
            Reverses the mutation applied to the solution.
        _reverse():
            Abstract method to be implemented by subclasses for reversing the mutation.
        _mutate_solution():
            Abstract method to be implemented by subclasses for applying the mutation.
        _is_possible():
            Abstract method to be implemented by subclasses for checking if the mutation is possible.
    """

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
