from dataclasses import dataclass


@dataclass
class Vehicle:
    """
    Vehicle class representing a vehicle used for deliveries.

    Args
    ----
        capacity (float): *q*<sub>j</sub> - vehicle package capacity in kilograms.
        fuel_consumption (float): *p*<sub>j</sub> - fuel consumption rate in liters per kilometer.
    """

    capacity: float
    fuel_consumption: float
