from dataclasses import dataclass

from model import Solution
from ga.mutations import *


@dataclass
class GAState:
    solution: Solution
    crossok: int
    crossall: int
    mutations = [
        CouriersMutation,
        NewCourierMutation,
        PackagesMutation,
        UsedVehiclesMutation,
        UnusedVehiclesMutation,
        RouteMutation,
    ]
    cpu_time: float
