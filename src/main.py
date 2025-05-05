import numpy as np
from generator import Generator
from problem_initializer import ProblemInitializer
from ga import GA
from ui import *
from operator import itemgetter


def main():
    n_couriers = 1
    n_vehicles = 1
    n_packages = 10

    problem = ProblemInitializer(n_couriers, n_vehicles, n_packages).get_problem()
    print(problem)

    generator = Generator(problem)
    solutions = generator.generate_many_feasible(num_to_find=1)

    ga = GA(problem, solutions)

    a, b = ga.run()
    print()
    print(f"BEFORE {ga.get_score(a)}")
    print(a)
    print(f"AFTER {ga.get_score(b)}")
    print(b)

    print(ga.get_score(a), ga.get_score(b))

    draw_comparison(a, b)
