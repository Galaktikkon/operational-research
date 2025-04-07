from typing import List, Dict, Tuple
from classes.problem_instance import ProblemInstance


class Solution:
    def __init__(
        self,
        problem: ProblemInstance,
        z_ij: Dict[Tuple[int, int], int],
        y_kj: Dict[Tuple[int, int], int],
        routes: Dict[int, List[int]],
        v_k: Dict[int, float],
    ):
        self.problem = problem
        self.z_ij = z_ij
        self.y_kj = y_kj
        self.routes = routes
        self.v_k = v_k

        self.x_uvj = self._calculate_x_uvj()
        self.t_i = self._calculate_courier_times()
        self.d_j = self._calculate_vehicle_distances()
        self.objective_value = self._calculate_objective()

    def _calculate_x_uvj(self) -> Dict[Tuple[int, int, int], int]:
        x = {}
        for vehicle_id, route in self.routes.items():
            if len(route) > 1:
                for i in range(len(route) - 1):
                    u, v = route[i], route[i + 1]
                    x[(u, v, vehicle_id)] = 1
        return x

    def _get_route_time(self, vehicle_id: int) -> float:
        route = self.routes.get(vehicle_id, [])
        total_time = 0.0
        if len(route) > 1:
            for i in range(len(route) - 1):
                u, v = route[i], route[i + 1]
                total_time += self.problem.travel_times.get((u, v), float("inf"))
        return total_time

    def _calculate_courier_times(self) -> Dict[int, float]:
        t_i = {courier_id: 0.0 for courier_id in self.problem.couriers}
        for (courier_id, vehicle_id), assigned in self.z_ij.items():
            if assigned == 1:
                route_time = self._get_route_time(vehicle_id)
                t_i[courier_id] = route_time
        return t_i

    def _calculate_vehicle_distances(self) -> Dict[int, float]:
        d_j = {vehicle_id: 0.0 for vehicle_id in self.problem.vehicles}
        for vehicle_id, route in self.routes.items():
            if len(route) > 1:
                for i in range(len(route) - 1):
                    u, v = route[i], route[i + 1]
                    d_j[vehicle_id] += self.problem.distances.get((u, v), 0)
        return d_j

    def _calculate_objective(self) -> float:
        salaries = sum(
            self.t_i[i] * self.problem.couriers[i].hourly_rate
            for i in self.problem.couriers
        )

        fuel_cost = self.problem.fuel_price * sum(
            self.problem.vehicles[j].fuel_consumption * self.d_j[j]
            for j in self.problem.vehicles
        )

        avg_service_time_penalty = 0
        if self.problem.all_package_ids:
            total_delay = sum(
                max(0, self.v_k[k] - self.problem.packages[k].start_time)
                for k in self.problem.all_package_ids
                if k in self.v_k
            )
            avg_service_time_penalty = self.problem.alpha * (
                total_delay / len(self.problem.all_package_ids)
            )

        return salaries + fuel_cost + avg_service_time_penalty
