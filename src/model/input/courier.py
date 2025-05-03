from dataclasses import dataclass


@dataclass
class Courier:
    hourly_rate: float
    work_limit: float
