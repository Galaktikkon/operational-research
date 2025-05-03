from typing import Literal

PackageType = Literal["delivery", "pickup"]


class Package:
    def __init__(
        self,
        address: int,
        weight: float,
        start_time: float,
        end_time: float,
        type: PackageType = "delivery",
    ):
        self.address = address  # h_k
        self.weight = weight  # w_k
        self.start_time = start_time  # a_k
        self.end_time = end_time  # b_k
        self.type = type  # 'delivery' or 'pickup'
