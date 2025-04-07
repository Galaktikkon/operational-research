from typing import List, Dict, Tuple
from classes.solution import Solution


class Checker:
    def __check_courier_vehicle_assignments(
        solution: Solution,
    ) -> Tuple[bool, List[str]]:
        """Checks courier-vehicle assignments constraints."""
        problem = solution.problem
        errors = []

        # Constraint: Each courier is assigned exactly one vehicle
        for i in problem.couriers:
            assigned_vehicles = sum(
                solution.z_ij.get((i, j), 0) for j in problem.vehicles
            )
            if assigned_vehicles != 1:
                errors.append(
                    f"Courier {i} is assigned {assigned_vehicles} vehicles (expected 1)."
                )

        # Constraint: Each vehicle is assigned exactly one courier
        for j in problem.vehicles:
            assigned_couriers = sum(
                solution.z_ij.get((i, j), 0) for i in problem.couriers
            )
            if assigned_couriers != 1:
                errors.append(
                    f"Vehicle {j} is assigned {assigned_couriers} couriers (expected 1)."
                )

        # Constraint: Courier must have permissions to drive the vehicle
        for (i, j), assigned in solution.z_ij.items():
            if assigned == 1 and problem.permissions.get((i, j), 0) == 0:
                errors.append(
                    f"Courier {i} is assigned to vehicle {j} but lacks permissions (r_{i},{j}=0)."
                )

        return not errors, errors

    def __check_package_assignments(solution: Solution) -> Tuple[bool, List[str]]:
        """Checks package-vehicle assignments constraints."""
        problem = solution.problem
        errors = []

        # Constraint: Each package is assigned to exactly one vehicle
        for k in problem.packages:
            assigned_vehicles = sum(
                solution.y_kj.get((k, j), 0) for j in problem.vehicles
            )
            if assigned_vehicles != 1:
                errors.append(
                    f"Package {k} is assigned to {assigned_vehicles} vehicles (expected 1)."
                )

        # Constraint: Vehicle assigned to a package must visit its address
        for (k, j), assigned in solution.y_kj.items():
            if assigned == 1:
                package_address = problem.packages[k].address
                visited_address = False
                route = solution.routes.get(j, [])
                if (
                    package_address in route
                    and package_address != problem.warehouse_node
                ):
                    visited_address = True

                if not visited_address:
                    arrives_at_address = any(
                        solution.x_uvj.get((u, package_address, j), 0) == 1
                        for u in problem.nodes
                    )
                    if not arrives_at_address:
                        errors.append(
                            f"Package {k} (address {package_address}) is assigned to vehicle {j}, but the vehicle does not visit this address."
                        )

        return not errors, errors

    def __check_courier_work_limits(solution: Solution) -> Tuple[bool, List[str]]:
        """Checks if couriers' work time exceeds their limits."""
        problem = solution.problem
        errors = []
        for i, courier in problem.couriers.items():
            if solution.t_i[i] > courier.work_limit:
                errors.append(
                    f"Courier {i} exceeded work time limit ({solution.t_i[i]} > {courier.work_limit})."
                )
        return not errors, errors

    def __check_time_windows(solution: Solution) -> Tuple[bool, List[str]]:
        """Checks time window constraints for deliveries/pickups."""
        problem = solution.problem
        errors = []

        # Constraint: a_k <= v_k <= b_k
        for k, package in problem.packages.items():
            if k not in solution.v_k:
                errors.append(f"Missing service time v_k for package {k}.")
                continue
            service_time = solution.v_k[k]
            if not (package.start_time <= service_time <= package.end_time):
                errors.append(
                    f"Service time for package {k} ({service_time}) is outside the window [{package.start_time}, {package.end_time}]."
                )

        # Constraint: Precedence for packages served consecutively by the same vehicle
        for j, route in solution.routes.items():
            current_time = 0
            if not route or route[0] != problem.warehouse_node:
                continue

            address_to_packages = {}
            for k, p in problem.packages.items():
                if p.address not in address_to_packages:
                    address_to_packages[p.address] = []
                if solution.y_kj.get((k, j), 0) == 1:
                    address_to_packages[p.address].append(k)

            last_node = route[0]
            for i in range(1, len(route)):
                current_node = route[i]
                travel_time = problem.travel_times.get(
                    (last_node, current_node), float("inf")
                )
                if travel_time == float("inf"):
                    errors.append(
                        f"No connection ({last_node}, {current_node}) in vehicle {j}'s route."
                    )
                    break

                arrival_time = current_time + travel_time

                if current_node in address_to_packages:
                    packages_at_node = address_to_packages[current_node]
                    max_service_start_time = arrival_time

                    for k in packages_at_node:
                        package = problem.packages[k]
                        service_time_vk = solution.v_k.get(k)

                        if service_time_vk is None:
                            continue

                        earliest_start = max(arrival_time, package.start_time)
                        if service_time_vk < earliest_start - 1e-6:
                            errors.append(
                                f"Package {k} (address {current_node}) serviced at {service_time_vk} by vehicle {j}, but earliest possible time is {earliest_start}."
                            )

                        max_service_start_time = max(
                            max_service_start_time, service_time_vk
                        )

                    current_time = max_service_start_time
                else:
                    current_time = arrival_time

                last_node = current_node

        return not errors, errors

    def __check_vehicle_capacity(solution: Solution) -> Tuple[bool, List[str]]:
        """Checks vehicle capacity constraints along routes."""
        problem = solution.problem
        errors = []

        for j, vehicle in problem.vehicles.items():
            route = solution.routes.get(j)
            if (
                not route
                or route[0] != problem.warehouse_node
                or route[-1] != problem.warehouse_node
            ):
                if route:
                    errors.append(
                        f"Vehicle {j}'s route does not start/end at the warehouse {problem.warehouse_node}: {route}"
                    )
                continue

            capacity = vehicle.capacity
            current_load = sum(
                problem.packages[k].weight
                for k in problem.delivery_packages
                if solution.y_kj.get((k, j), 0) == 1
            )

            if current_load > capacity + 1e-6:
                errors.append(
                    f"Vehicle {j} exceeds capacity ({capacity}) when leaving the warehouse (load: {current_load})."
                )
                continue

            for i in range(1, len(route)):
                node = route[i]

                delivered_weight = sum(
                    problem.packages[k].weight
                    for k in problem.delivery_packages
                    if problem.packages[k].address == node
                    and solution.y_kj.get((k, j), 0) == 1
                )
                current_load -= delivered_weight

                picked_up_weight = sum(
                    problem.packages[k].weight
                    for k in problem.pickup_packages
                    if problem.packages[k].address == node
                    and solution.y_kj.get((k, j), 0) == 1
                )
                current_load += picked_up_weight

                if not (0 - 1e-6 <= current_load <= capacity + 1e-6):
                    errors.append(
                        f"Vehicle {j} has invalid load ({current_load}) after leaving node {node} (capacity: {capacity})."
                    )
                    break

        return not errors, errors

    def __check_route_structure(solution: Solution) -> Tuple[bool, List[str]]:
        """Checks route structure constraints (flow)."""
        problem = solution.problem
        errors = []

        x = solution.x_uvj

        for j in problem.vehicles:
            departures = sum(
                x.get((problem.warehouse_node, v, j), 0)
                for v in problem.nodes
                if v != problem.warehouse_node
            )
            if departures > 1:
                errors.append(
                    f"Vehicle {j} departs from the warehouse {departures} times (max 1)."
                )

            arrivals = sum(
                x.get((u, problem.warehouse_node, j), 0)
                for u in problem.nodes
                if u != problem.warehouse_node
            )
            if departures != arrivals:
                errors.append(
                    f"Vehicle {j} has {departures} departures and {arrivals} returns to the warehouse."
                )

            for v_node in problem.nodes:
                if v_node == problem.warehouse_node:
                    continue

                in_flow = sum(x.get((u, v_node, j), 0) for u in problem.nodes)
                out_flow = sum(x.get((v_node, w, j), 0) for w in problem.nodes)

                if in_flow != out_flow:
                    errors.append(
                        f"Flow mismatch for vehicle {j} at node {v_node} (in: {in_flow}, out: {out_flow})."
                    )

        return not errors, errors

    def is_feasible(solution: Solution) -> Tuple[bool, Dict[str, List[str]]]:
        """Checks if the entire solution is feasible."""
        all_errors = {}

        feasible_cv, errors_cv = Checker.__check_courier_vehicle_assignments(solution)
        if not feasible_cv:
            all_errors["CourierVehicleAssignments"] = errors_cv

        feasible_pa, errors_pa = Checker.__check_package_assignments(solution)
        if not feasible_pa:
            all_errors["PackageAssignments"] = errors_pa

        feasible_wl, errors_wl = Checker.__check_courier_work_limits(solution)
        if not feasible_wl:
            all_errors["CourierWorkLimits"] = errors_wl

        feasible_tw, errors_tw = Checker.__check_time_windows(solution)
        if not feasible_tw:
            all_errors["TimeWindows"] = errors_tw

        feasible_cap, errors_cap = Checker.__check_vehicle_capacity(solution)
        if not feasible_cap:
            all_errors["VehicleCapacity"] = errors_cap

        feasible_rs, errors_rs = Checker.__check_route_structure(solution)
        if not feasible_rs:
            all_errors["RouteStructure"] = errors_rs

        return not all_errors, all_errors
