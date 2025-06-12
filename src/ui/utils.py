import tkinter as tk
from tkinter import messagebox
from problem_initializer import ProblemInitializer


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


def set_text(entyr, text):
    entyr.delete(0, tk.END)
    entyr.insert(0, text)


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
