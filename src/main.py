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
    solutions = generator.generate_many_feasible(num_to_find=1)

    initial_population = solutions

    ga = GA(problem, initial_population)

    solutions = [(s, ga.get_score(s)) for s in solutions]
    solutions.sort(key=itemgetter(1))

    if len(solutions):
        draw_solution(solutions[0][0])

    for idx, (solution, score) in enumerate(solutions, start=1):
        print(f"\n--- Solution {idx} --- {score:.2f}")
        print(solution)
