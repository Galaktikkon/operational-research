from dataclasses import dataclass

from model import Solution
from ga.mutations import (
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
