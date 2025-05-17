from generator import Generator
from problem_initializer import ProblemInitializer
from ga import GA
from ui import *


def main():
    n_couriers = 1
    n_vehicles = 1
    n_packages = 20

    problem = ProblemInitializer(n_couriers, n_vehicles, n_packages).get_problem()
    print(problem)

    generator = Generator(problem)
    solutions = generator.generate_many_feasible(num_to_find=20)

    ga = GA(problem, solutions)

    a, b = ga.run()
    print()
    print(f"BEFORE {ga.get_cost(a)}")
    print(a)
    print(f"AFTER {ga.get_cost(b)}")
    print(b)

    print(ga.get_cost(a), ga.get_cost(b))

    draw_comparison(a, b)
