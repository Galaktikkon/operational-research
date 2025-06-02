from dataclasses import dataclass

from src.model import Solution
from src.ga.mutations import (
    CouriersMutation,
    PackagesMutation,
    RouteMutation,
    UnusedVehiclesMutation,
    UsedVehiclesMutation,
)


@dataclass
class GAState:
    solution: Solution
    crossok: int
    crossall: int
    mutations = [
        CouriersMutation,
        PackagesMutation,
        UsedVehiclesMutation,
        UnusedVehiclesMutation,
        RouteMutation,
    ]
