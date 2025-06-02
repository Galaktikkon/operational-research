from dataclasses import dataclass
from typing import Literal

PackageType = Literal["delivery", "pickup"]


@dataclass
class Package:
    """
    Package class representing a package to be delivered or picked up.

    Args
    ----
        address (int): *h*<sub>k</sub> - package destination address (as an integer identifier).
        weight (float): *w*<sub>k</sub> - Package weight in kilograms.
        start_time (float): *a*<sub>k</sub> - earliest time (in hours) when the package can be handled.
        end_time (float): *b*<sub>k</sub> - latest time (in hours) by which the package must be handled.
        type (PackageType, optional): Type of package, either "delivery" or "pickup". Defaults to "delivery".
    """

    address: int
    weight: float
    start_time: float
    end_time: float
    type: PackageType = "delivery"

    @classmethod
    def from_dict(cls, dictionary):
        return cls(
            dictionary["address"],
            dictionary["weight"],
            dictionary["start_time"],
            dictionary["end_time"],
            dictionary["type"],
        )

    def to_dict(self):
        return {
            "address": int(self.address),
            "weight": float(self.weight),
            "start_time": float(self.start_time),
            "end_time": float(self.end_time),
            "type": self.type,
        }
