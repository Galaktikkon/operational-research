from dataclasses import dataclass


@dataclass
class Courier:
    """
    Courier class representing a courier who delivers packages.

    Args
    ----
        hourly_rate (float): *c*<sub>i</sub> - hourly rate of the courier in currency units.
        work_limit (float): *b*<sub>i</sub> - maximum working hours allowed for the courier.
    """

    hourly_rate: float
    work_limit: float
