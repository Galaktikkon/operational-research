from dataclasses import dataclass
from src.model import Problem

@dataclass
class LoadedProblem:
    problem: Problem
    solutions_num: int
    attempts_num: int
    iterations_num: int
    