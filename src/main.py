from time import perf_counter

from classes.generator import Generator
from classes.courier import Courier
from classes.package import Package
from classes.problem_instance import ProblemInstance
from classes.vehicle import Vehicle


if __name__ == "__main__":
    couriers_data = [Courier(id=1, hourly_rate=20, work_limit=480)]
    vehicles_data = [Vehicle(id=101, capacity=100, fuel_consumption=0.1)]
    packages_data = [
        Package(
            id=1001, address=1, weight=50, start_time=0, end_time=60, type="delivery"
        )
    ]
    permissions_data = {(1, 101): 1}
    travel_times_data = {(0, 1): 10.0, (1, 0): 10.0, (0, 0): 0.0, (1, 1): 0.0}
    distances_data = {(0, 1): 5.0, (1, 0): 5.0, (0, 0): 0.0, (1, 1): 0.0}
    fuel_price_val = 6.5
    alpha_val = 0.1
    warehouse_node_val = 0

    problem_instance = ProblemInstance(
        couriers=couriers_data,
        vehicles=vehicles_data,
        packages=packages_data,
        permissions=permissions_data,
        travel_times=travel_times_data,
        distances=distances_data,
        fuel_price=fuel_price_val,
        alpha=alpha_val,
        warehouse_node=warehouse_node_val,
    )

    start_time = perf_counter()
    solutions = Generator.generate_many_feasible(problem_instance, 3, 10e4)
    end_time = perf_counter()

    if solutions:
        for idx, solution in enumerate(solutions, start=1):
            print(f"\n--- Solution {idx} ---")
            print("\nCourier-Vehicle Assignments (z_ij):")
            print(solution.z_ij)
            print("\nPackage-Vehicle Assignments (y_kj):")
            print(solution.y_kj)
            print("\nRoutes:")
            print(solution.routes)
            print("\nService Times (v_k):")
            print(solution.v_k)
            print("\nCourier Work Times (t_i):")
            print(solution.t_i)
            print("\nVehicle Distances (d_j):")
            print(solution.d_j)
            print(f"\nObjective Function Value: {solution.objective_value:.2f}")
            print(f"Time elapsed: {(end_time - start_time):.4f} s")
