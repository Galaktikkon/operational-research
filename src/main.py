from time import perf_counter

from generator import Generator
from problem_initializer import ProblemInitializer


def main():
    problem = ProblemInitializer().get_problem()
    generator = Generator(problem)

    start_time = perf_counter()
    solutions = generator.generate_many_feasible(2)
    end_time = perf_counter()

    for idx, solution in enumerate(solutions, start=1):
        print(f"\n--- Solution {idx} ---")
        print("\nRoute-Vehicle Assignments (x_uvj):")
        print(solution.x_uvj)
        print("\nPackage-Vehicle Assignments (y_kj):")
        print(solution.y_kj)
        print("\nCourier-Vehicle Assignments (z_ij):")
        print(solution.z_ij)

    print(f"Time elapsed: {(end_time - start_time):.4f}s")
