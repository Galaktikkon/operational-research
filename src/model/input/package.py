from typing import Literal
from dataclasses import dataclass

PackageType = Literal["delivery", "pickup"]


@dataclass
class Package:
    address: int
    weight: float
    start_time: float
    end_time: float
    type: PackageType = "delivery"
