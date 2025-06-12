import functools
import sys
from copy import deepcopy

import numpy as np

from model.problem import Problem
from model.solution import Solution
from solution_checker import SolutionChecker

from .mutations import (
    Mutation,
    RouteMutation,
    UnusedVehiclesMutation,
    UsedVehiclesMutation,
    PackagesMutation,
    CouriersMutation,
)

from ga.ga_state import GAState

crossok = 0
crossnok = 0


class GA:
    """
    Genetic Algorithm for solving the problem of optimizing courier and vehicle assignments.
    This class implements the genetic algorithm with crossover and mutation operations to find
    optimal solutions for the given problem.
    Attributes:
        problem (Problem): The problem instance containing couriers, vehicles, and packages.
        checker (SolutionChecker): An instance to check the feasibility of solutions.
        C (float): A constant used in cost calculation.
        alpha (float): A parameter used in delay cost calculation.
        initial_population (list[Solution]): The initial population of solutions to start the algorithm.
    Methods:
        get_cost(solution: Solution) -> float:
            Calculate the cost of a given solution.
        crossover(s1: Solution, s2: Solution) -> tuple[Solution, Solution]:
            Perform crossover between two solutions to create new solutions.
        mutation(solution: Solution) -> Solution:
            Apply mutation to a solution to create a new solution.
        run(max_iter=1000) -> tuple[Solution, Solution]:
            Execute the genetic algorithm to optimize the solution over a specified number of iterations.
    """

    def __init__(
        self,
        problem: Problem,
        initial_population: list[Solution],
        C,
        alpha,
    ):
        self.initial_population = initial_population
        self.mutations: list[type[Mutation]] = [
            CouriersMutation,
            UsedVehiclesMutation,
            UnusedVehiclesMutation,
            PackagesMutation,
            RouteMutation,
        ]
        self.problem = problem
        self.checker = SolutionChecker(problem)

        self.C = C
        self.alpha = alpha

        self._cost_function_runs = 0

    @functools.cache
    def get_cost(self, solution: Solution):
        """
        Calculate the cost of a solution.
        The cost is calculated as follows:
        - Rates of couriers: sum of hourly rates of couriers multiplied by the time spent
        - Fuel cost: sum of fuel consumption of vehicles multiplied by the distance traveled
        - Delay: alpha divided by the number of packages multiplied by the sum of delays

        :param solution: Solution to calculate the cost for
        :return: Total cost of the solution
        """
        c_i = np.array([c.hourly_rate / 60 for c in self.problem.couriers])
        p_j = np.array([v.fuel_consumption for v in self.problem.vehicles])

        a_k = np.array([p.start_time for p in self.problem.packages])

        rates = solution.get_t_i() @ c_i
        fuel_cost = self.C * (p_j @ solution.get_d_j())
        delay = self.alpha / self.problem.n_packages * np.sum(solution.get_v_k() - a_k)

        self._cost_function_runs += 1

        return rates + fuel_cost + delay

    def crossover(self, s1: Solution, s2: Solution):
        """Perform crossover between two solutions.
        This method attempts to create two new solutions by combining the couriers and vehicles
        from the two parent solutions.

        Args:
            s1 (Solution): The first parent solution.
            s2 (Solution): The second parent solution.

        Returns:
            tuple: A tuple containing two new solutions (a, b). If crossover fails after 10 attempts,
                   returns (None, None).
        """
        global crossok, crossnok
        for _ in range(10):
            a, b = self._crossover(s1, s2)
            if a is None and b is None:
                crossnok += 1
            else:
                crossok += 1
                return a, b
        return None, None

    def _crossover(self, s1: Solution, s2: Solution):
        """Internal method to perform crossover between two solutions.
        This method combines the couriers and vehicles from two solutions while respecting the
        permissions of couriers to vehicles. It creates two new solutions based on the input solutions.

        Args:
            s1 (Solution): The first solution.
            s2 (Solution): The second solution.

        Returns:
            tuple: A tuple containing two new solutions (a, b). If either solution is infeasible,
                   returns (None, None).
        """
        problem = self.problem

        z_j1 = s1.z_j.copy()
        y_k1 = s1.y_k.copy()

        z_j2 = s2.z_j.copy()
        y_k2 = s2.y_k.copy()

        # Get used and unused and used couriers and vehicles from both solutions
        s1_used_couriers = np.unique(z_j1)
        s1_used_couriers = s1_used_couriers[s1_used_couriers != -1]
        s1_unused_couriers = np.setdiff1d(
            np.arange(problem.n_couriers), s1_used_couriers, assume_unique=True
        )

        s2_used_couriers = np.unique(z_j2)
        s2_used_couriers = s2_used_couriers[s2_used_couriers != -1]
        s2_unused_couriers = np.setdiff1d(
            np.arange(problem.n_couriers), s2_used_couriers, assume_unique=True
        )

        # Get used vehicles from both solutions
        s1_used_vehicles = np.unique(y_k1)
        s2_used_vehicles = np.unique(y_k2)

        a_x_jv = s1.x_jv.copy()
        a_y_k = y_k1.copy()
        a_z_j = np.full_like(z_j1, -1)

        b_x_jv = s2.x_jv.copy()
        b_y_k = y_k2.copy()
        b_z_j = np.full_like(z_j2, -1)

        a_set = set()

        s2_used_set = set(s2_used_couriers)
        s2_unused_set = set(s2_unused_couriers)

        b_set = set()

        s1_used_set = set(s1_used_couriers)
        s1_unused_set = set(s1_unused_couriers)

        # Assign couriers to vehicles in a way that respects permissions
        for j in np.random.permutation(s1_used_vehicles):
            vehicle_travel_time = s1.get_l_vj()[problem.graph.warehouse, j]
            for _ in range(2 * len(s2_used_set)):
                i = np.random.choice(list(s2_used_set))
                c = problem.couriers[i]
                if (
                    (i, j) in problem.permissions
                    and i not in a_set
                    and vehicle_travel_time <= c.work_limit * 60
                ):
                    a_set.add(i)
                    s2_used_set.remove(i)
                    a_z_j[j] = i
                    break
            else:
                # If no used couriers are available, try unused couriers
                for _ in range(2 * len(s2_unused_set)):
                    i = np.random.choice(list(s2_unused_set))
                    c = problem.couriers[i]
                    if (
                        (i, j) in problem.permissions
                        and i not in a_set
                        and vehicle_travel_time <= c.work_limit * 60
                    ):
                        a_set.add(i)
                        s2_unused_set.remove(i)
                        a_z_j[j] = i
                        break
                else:
                    break

        # Assign couriers to vehicles in b in a way that respects permissions
        for j in np.random.permutation(s2_used_vehicles):
            vehicle_travel_time = s2.get_l_vj()[problem.graph.warehouse, j]
            for _ in range(2 * len(s1_used_set)):
                i = np.random.choice(list(s1_used_set))
                c = problem.couriers[i]
                if (
                    (i, j) in problem.permissions
                    and i not in b_set
                    and vehicle_travel_time <= c.work_limit * 60
                ):
                    b_set.add(i)
                    s1_used_set.remove(i)
                    b_z_j[j] = i
                    break
            else:
                # If no used couriers are available, try unused couriers
                for _ in range(2 * len(s1_unused_set)):
                    i = np.random.choice(list(s1_unused_set))
                    c = problem.couriers[i]
                    if (
                        (i, j) in problem.permissions
                        and i not in b_set
                        and vehicle_travel_time <= c.work_limit * 60
                    ):
                        b_set.add(i)
                        s1_unused_set.remove(i)
                        b_z_j[j] = i
                        break
                else:
                    break

        a = Solution(problem, a_x_jv, a_y_k, a_z_j) if -1 not in a_z_j[a_y_k] else None
        b = Solution(problem, b_x_jv, b_y_k, b_z_j) if -1 not in b_z_j[b_y_k] else None

        if a is not None and not self.checker.is_feasible(a):
            a = None

        if b is not None and not self.checker.is_feasible(b):
            b = None

        return a, b

    def mutation(self, solution: Solution):
        """Perform mutations on a solution.
        This method applies various mutation strategies to the given solution.
        Args:
            solution (Solution): The solution to mutate.
        Returns:
            Solution: The mutated solution if a feasible mutation is found, otherwise the original solution.
        """
        x_jv = solution.x_jv
        y_k = solution.y_k
        z_j = solution.z_j

        solution = Solution(solution.problem, x_jv.copy(), y_k.copy(), z_j.copy())
        original = Solution(solution.problem, x_jv.copy(), y_k.copy(), z_j.copy())

        available_mutations = []

        for mutation_class in self.mutations:
            if mutation_class is not RouteMutation:
                available_mutations += [mutation_class(solution)]
            else:
                available_mutations += [
                    mutation_class(solution, j)
                    for j in np.random.permutation(np.unique(y_k))
                ]

        mutation_order = np.random.permutation(np.arange(len(available_mutations)))

        for m in mutation_order:
            mutation: Mutation = available_mutations[m]

            if not mutation.is_possible():
                continue

            mutation.mutate_solution()
            assert solution != original

            if self.checker.is_feasible(solution):
                return solution
            else:
                mutation.reverse()
                assert solution == original

        return solution

    def run(self, max_iter=1000, verbose=True):
        """Run the genetic algorithm to optimize the solution.
        This method initializes the population, performs crossover and mutation operations,
        and iteratively improves the solutions until the maximum number of iterations is reached.

        Args:
            max_iter (int, optional): The maximum number of iterations to run the algorithm. Defaults to 1000.

        Returns:
            tuple: A tuple containing the initial best solution and the final best solution found.
                   The first element is the initial best solution, and the second element is the final best solution.
        """

        solutions = self.initial_population
        l = len(solutions)  # noqa: E741

        solutions.sort(key=lambda s: self.get_cost(s))
        initial_best = deepcopy(solutions[0])
        yield GAState(initial_best, crossok, crossok + crossnok)

        pairs = [(i, j) for i in range(l // 2) for j in range(i + 1, l // 2)]

        def get_pairs():
            index = np.random.randint(low=0, high=len(pairs), size=(l // 2))
            return [pairs[i] for i in index]

        for i in range(1, max_iter + 1):
            solutions.sort(key=lambda s: self.get_cost(s))
            yield GAState(deepcopy(solutions[0]), crossok, crossok + crossnok)
            new = [self.crossover(solutions[i], solutions[j]) for i, j in get_pairs()]
            new = [t[0] for t in new] + [t[1] for t in new]
            new = [n for n in new if n]
            new = [self.mutation(n) for n in new]

            # print("Crossovers", crossok, "/", crossok + crossnok)
            # new = [self.mutation(n) for n in new if n]
            # new = [self.mutation(n) for n in solutions[: l // 2]]
            o = 0
            while len(new) + l // 2 < l:
                new.append(solutions[l // 2 + o])
                o += 1

            solutions = solutions[: l // 2] + new
