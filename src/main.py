import numpy as np
from generator import Generator
from problem_initializer import ProblemInitializer
from ga import GA
from ui import *
from operator import itemgetter


def main():
    problem = ProblemInitializer().get_problem()
    print(problem)

    generator = Generator(problem)
    solutions = generator.generate_many_feasible(num_to_find=10)

    ga = GA(problem, solutions)

    solutions.sort(key=lambda s: ga.get_score(s))
    draw_solution(solutions[0])

    draw_solution(ga.run())
