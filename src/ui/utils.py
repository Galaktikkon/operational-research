import tkinter as tk
from tkinter import messagebox


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
        return
    return data
