from time import perf_counter

from generator import Generator
from problem_initializer import ProblemInitializer


def main():
    problem = ProblemInitializer().get_problem()
    generator = Generator(problem)

    print(problem)

    start_time = perf_counter()
    solutions = generator.generate_many_feasible(max_attempts=100)
    end_time = perf_counter()

    for idx, solution in enumerate(solutions, start=1):
        print(f"\n--- Solution {idx} ---")
        print(solution)
        break

    print(f"Time elapsed: {(end_time - start_time):.4f}s")
