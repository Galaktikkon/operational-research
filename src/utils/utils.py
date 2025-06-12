import json
import inspect
import sys

import numpy as np

from model import *


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

    for key, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            continue

        expected_type = param.annotation
        actual_value = config[key]

        if not isinstance(actual_value, expected_type):
            print(
                f"Type mismatch for '{key}': expected {expected_type}, got {type(actual_value)}",
                file=sys.stderr,
            )
            return False

    return True


def save_to_json(self: Problem, path):
    problem_data = {}
    problem_data["couriers"] = [courier.to_dict() for courier in self.couriers]
    problem_data["vehicles"] = [vehicle.to_dict() for vehicle in self.vehicles]
    problem_data["packages"] = [package.to_dict() for package in self.packages]
    problem_data["permissions"] = [
        {"courier": courier, "vehicle": vehicle}
        for courier, vehicle in self.permissions
    ]
    problem_data["graph"] = self.graph.to_dict()
    with open(path, "w") as f:
        json.dump(problem_data, f, indent=2)


def load_from_json(json_file):
    couriers = []
    vehicles = []
    permissions = []
    packages = []
    graph = None

    with open(json_file, "r") as f:
        problem_data = json.load(f)

    for courier in problem_data["couriers"]:
        couriers.append(Courier.from_dict(courier))

    for vehicle in problem_data["vehicles"]:
        vehicles.append(Vehicle.from_dict(vehicle))

    for permission in problem_data["permissions"]:
        permissions.append((permission["courier"], permission["vehicle"]))

    for package in problem_data["packages"]:
        packages.append(Package.from_dict(package))

    graph = problem_data["graph"]
    graph = Graph.from_dict(graph)

    return Problem(
        couriers,
        vehicles,
        packages,
        permissions,
        graph,
    )
