GENERATOR_DEFAULTS = {
    "couriers": 5,
    "vehicles": 3,
    "packages": 20,
    "max coord": 50,
    "time dist coeff": 0.5,
    "permission proba": 1,
    "pickup delivery proba": 0.5,
}

GENERATOR_RANGE_DEFAULTS = {
    "rate_min": 0,
    "rate_max": 100,
    "work limit_min": 2,
    "work limit_max": 8,
    "capacity_min": 10,
    "capacity_max": 100,
    "fuel_min": 0,
    "fuel_max": 20,
    "weight_min": 0,
    "weight_max": 10,
    "package start time_min": 0,
    "package start time_max": 0,
    "package end time_min": 100,
    "package end time_max": 100,
}
SIMULATION_DEFAULTS = {
    "initial population": 10,
    "attempts": 1000,
    "iterations": 500,
    "C": 1.2,
    "alpha": 0.9,
    "animation delay": 50,
}
GENERATOR_SINGLE_FIELDS = [
    "couriers",
    "vehicles",
    "packages",
    "max coord",
    "time dist coeff",
    "permission proba",
    "pickup delivery proba",
]

GENERATOR_RANGE_FIELDS = [
    "rate",
    "work limit",
    "capacity",
    "fuel",
    "weight",
    "package start time",
    "package end time",
]

GENERATOR_FIELDS = (
    GENERATOR_SINGLE_FIELDS
    + [f"{f}_min" for f in GENERATOR_RANGE_FIELDS]
    + [f"{f}_max" for f in GENERATOR_RANGE_FIELDS]
)

SIMULATION_FIELDS = [
    "initial population",
    "attempts",
    "iterations",
    "C",
    "alpha",
    "animation delay",
]
