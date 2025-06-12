import re
import tkinter as tk
from tkinter import messagebox
from problem_initializer import ProblemInitializer
import matplotlib.pyplot as plt


class ValidationError(Exception):
    pass


def get_number(text):
    try:
        number = int(text)
        return number
    except ValueError:
        try:
            number = float(text)
            return number
        except ValueError:
            raise ValidationError(f"Invalid number: '{text}'")


def set_text(entry, text):
    entry.delete(0, tk.END)
    entry.insert(0, text)


def validate_form(form, fields):
    data = {}
    try:
        for field in fields:
            val = form[field].get()
            number = get_number(val)
            data[field] = number
    except ValidationError as e:
        messagebox.showerror("Invalid input", str(e))
        return {}
    return data


def create_initializer(settings: dict):
    return ProblemInitializer(
        settings["couriers"],
        settings["vehicles"],
        settings["packages"],
        settings["max coord"],
        (settings["rate_min"], settings["rate_max"]),
        (settings["work limit_min"], settings["work limit_max"]),
        (settings["capacity_min"], settings["capacity_max"]),
        (settings["fuel_min"], settings["fuel_max"]),
        (settings["weight_min"], settings["weight_max"]),
        (settings["package start time_min"], settings["package start time_max"]),
        (settings["package end time_min"], settings["package end time_max"]),
        settings["time dist coeff"],
        settings["permission proba"],
        settings["pickup delivery proba"],
    )


def draw_solution_to_axis(solution, axis):
    points = solution.problem.graph.points.T
    axis.scatter(points[0], points[1], s=60)

    w = solution.problem.graph.warehouse
    axis.scatter(points[0][w], points[1][w], s=65, c="red")

    for j in range(solution.problem.n_vehicles):
        for u, v in zip(solution.x_jv[j], solution.x_jv[j, 1:]):
            axis.arrow(
                *points[:, u],
                *(points[:, v] - points[:, u]),
                color=f"C{j}",
                head_width=0.6,
                length_includes_head=True,
            )
            if v == solution.problem.graph.warehouse:
                break

    for i in range(points.shape[1]):
        axis.annotate(f"{i}", (points[0][i], points[1][i]))


def get_mpl_color(i):
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    return colors[i % len(colors)]


def format_mutation_name(m):
    m = m.__name__ if type(m) != str else m
    return re.sub("([a-z])([A-Z])", r"\1 \2", m)
