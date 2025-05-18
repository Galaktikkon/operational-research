from generator import Generator
from problem_initializer import ProblemInitializer
from ga import GA
from ui import *


def main(
    n_couriers=50,
    n_vehicles=50,
    n_packages=100,
    num_to_find=int(1e6),
    max_attempts=int(1e6),
    max_iter=10000,
):

    problem = ProblemInitializer(n_couriers, n_vehicles, n_packages).get_problem()
    print(problem)

    generator = Generator(problem)
    solutions = generator.generate_many_feasible(num_to_find, max_attempts)

    ga = GA(problem, solutions)

    a, b = ga.run(max_iter=max_iter)
    print()
    print(f"BEFORE {ga.get_cost(a)}")
    print(a)
    print(f"AFTER {ga.get_cost(b)}")
    print(b)

    print(ga.get_cost(a), ga.get_cost(b))

    draw_comparison(a, b)
