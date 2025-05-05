import numpy as np
from model.problem import Problem


def calculate_vehicle_route(problem: Problem, y_k, j):
    route = np.full(problem.n_nodes + 1, problem.graph.warehouse, dtype=int)
    vehicle_packages = np.where(y_k == j)[0]

    vehicle_route = np.unique([problem.packages[k].address for k in vehicle_packages])

    vehicle_route = np.random.permutation(vehicle_route)

    for v_i, v in enumerate(vehicle_route, start=1):
        route[v_i] = v

    return route
