import inspect
import sys

import numpy as np

from model.problem import Problem


def calculate_vehicle_route(problem: Problem, y_k, j):
    """
    Calculate the route for a vehicle based on the assignments of packages to vehicles.

    Args:
        problem (Problem): The problem instance containing the graph and warehouse information.
        y_k (np.ndarray): Array indicating the vehicle assignment for each package.
        j (int): The index of the vehicle for which to calculate the route.

    Returns:
        np.ndarray: The route for the vehicle.
    """
    route = np.full(problem.n_nodes + 1, problem.graph.warehouse, dtype=int)
    vehicle_packages = np.where(y_k == j)[0]

    vehicle_route = np.unique([problem.packages[k].address for k in vehicle_packages])

    vehicle_route = np.random.permutation(vehicle_route)

    for v_i, v in enumerate(vehicle_route, start=1):
        route[v_i] = v

    return route


def validate_config(config: dict, func: callable) -> bool:
    sig = inspect.signature(func)
    expected_params = set(sig.parameters.keys())
    config_keys = set(config.keys())

    missing_keys = expected_params - config_keys
    extra_keys = config_keys - expected_params

    if missing_keys or extra_keys:
        print("Config keys do not match func() parameters!", file=sys.stderr)
        if missing_keys:
            print(f"Missing keys: {missing_keys}", file=sys.stderr)
        if extra_keys:
            print(f"Extra keys: {extra_keys}", file=sys.stderr)
        return False

    return True
