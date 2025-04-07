from typing import List, Dict, Tuple

from classes.courier import Courier
from classes.package import Package
from classes.vehicle import Vehicle


class ProblemInstance:
    def __init__(
        self,
        couriers: List[Courier],
        vehicles: List[Vehicle],
        packages: List[Package],
        permissions: Dict[Tuple[int, int], int],
        travel_times: Dict[Tuple[int, int], float],
        distances: Dict[Tuple[int, int], float],
        fuel_price: float,  # C
        alpha: float,  # alpha
        warehouse_node: int = 0,
    ):
        self.couriers = {c.id: c for c in couriers}
        self.vehicles = {v.id: v for v in vehicles}
        self.packages = {p.id: p for p in packages}

        self.permissions = permissions  # R[i, j] = 1 if courier i can drive vehicle j
        self.travel_times = travel_times
        self.distances = distances
        self.fuel_price = fuel_price
        self.alpha = alpha
        self.warehouse_node = warehouse_node

        self.n = len(self.couriers)
        self.m = len(self.vehicles)
        self.num_packages = len(self.packages)

        self.nodes = set([warehouse_node]) | {p.address for p in self.packages.values()}

        self.delivery_packages = {
            p.id for p in self.packages.values() if p.type == "delivery"
        }
        self.pickup_packages = {
            p.id for p in self.packages.values() if p.type == "pickup"
        }
        self.all_package_ids = set(self.packages.keys())

        self.M = 0
        if self.packages:
            if self.packages.values():
                max_b_k = max(p.end_time for p in self.packages.values())
            else:
                max_b_k = 0

            max_s_kl = 0

            if self.travel_times:
                for p1 in self.packages.values():
                    for p2 in self.packages.values():
                        loc1 = p1.address
                        loc2 = p2.address

                        if (loc1, loc2) in self.travel_times:
                            max_s_kl = max(
                                max_s_kl, self.travel_times.get((loc1, loc2), 0)
                            )

            self.M = max_b_k + max_s_kl + 1
