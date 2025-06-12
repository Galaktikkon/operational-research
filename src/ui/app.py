import re

import tkinter as tk
from tkinter import messagebox

from problem_initializer import ProblemInitializer
from ga.mutations import (
    RouteMutation,
    UnusedVehiclesMutation,
    UsedVehiclesMutation,
    PackagesMutation,
    CouriersMutation,
    Mutation,
)

from .utils import *
from .animation_popup import AnimationPopup


PROBLEM_FIELDS = ["couriers", "vehicles", "packages"]
SIMULATION_FIELDS = ["solutions", "attempts", "iterations"]


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        self.problem = None
        self.initializer = ProblemInitializer()

        self.json_path = "config/base.json"

        self.available_mutations: list[type[Mutation]] = [
            RouteMutation,
            UnusedVehiclesMutation,
            UsedVehiclesMutation,
            PackagesMutation,
            CouriersMutation,
        ]

        self.status_label = tk.Label(
            root,
            text="Problem not loaded or generated",
            font=("Arial", 12),
            fg="#555",
            bg="#f0f0f0",
        )
        self.status_label.pack(pady=10)

        top_frame = tk.Frame(root, bg="#f0f0f0")
        top_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)

        self.problem_panel = tk.LabelFrame(
            top_frame,
            text="Problem Data",
            bg="#f0f0f0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        self.problem_panel.grid(row=0, column=0, sticky="nsew", padx=10)

        self.simulation_panel = tk.LabelFrame(
            top_frame,
            text="Simulation Data",
            bg="#f0f0f0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        self.simulation_panel.grid(row=0, column=1, sticky="nsew", padx=10)

        bottom_frame = tk.Frame(root, bg="#f0f0f0")
        bottom_frame.pack(padx=10, pady=(0, 20), fill="both", expand=False)

        self.mutations_frame = tk.LabelFrame(
            bottom_frame,
            text="Mutations",
            bg="#f0f0f0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        self.mutations_frame.pack(side="left", expand=True, fill="both", padx=10)
        self.create_mutation_inputs()

        btn_frame = tk.LabelFrame(
            bottom_frame,
            text="Actions",
            bg="#f0f0f0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        btn_frame.pack(side="left", expand=True, fill="both", padx=10)

        btn_style = {
            "width": 20,
            "font": ("Arial", 12, "bold"),
            "bg": "#4caf50",
            "fg": "white",
            "activebackground": "#45a049",
            "relief": "raised",
            "bd": 3,
        }

        buttons = [
            ("Load", self.load, "normal"),
            ("Generate", self.generate, "normal"),
            ("Save", self.save, "normal"),
            ("Simulate", self.simulate, "disabled"),
        ]

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_rowconfigure(0, weight=1)
        btn_frame.grid_rowconfigure(1, weight=1)
        for idx, (text, cmd, state) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=cmd, state=state, **btn_style)
            row = idx // 2
            col = idx % 2
            btn.grid(row=row, column=col, padx=15, pady=10, sticky="")
            setattr(self, f"btn_{text.lower().replace(' ', '_')}", btn)

        self.problem_form = self.setup_problem_frame()
        self.simulation_form = self.setup_simulation_frame()

        self.udpate_state()

        self.animation_popups = []
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)

    def create_mutation_inputs(self):
        for idx, mutation_cls in enumerate(self.available_mutations):
            var = tk.StringVar(value="0.5")

            def update_value(var=var, mutation_cls=mutation_cls):
                try:
                    value = float(var.get())
                    if 0 <= value <= 1:
                        mutation_cls.proba = value
                    else:
                        mutation_cls.proba = 0
                except ValueError:
                    mutation_cls.proba = 0

            tk.Label(
                self.mutations_frame,
                text=re.sub("([a-z])([A-Z])", r"\1 \2", mutation_cls.__name__),
                font=("Arial", 11),
                bg="#f0f0f0",
                anchor="w",
                justify="left",
            ).grid(row=idx, column=0, sticky="w", padx=5, pady=5)

            entry = tk.Entry(
                self.mutations_frame, font=("Arial", 11), textvariable=var, width=8
            )
            entry.grid(row=idx, column=1, padx=5, pady=5)
            var.trace_add(
                "write", lambda *args, v=var, cls=mutation_cls: update_value(v, cls)
            )

    def _problem_ready(self):
        return self.problem is not None

    def udpate_state(self):
        if self.problem is not None:
            self.status_label.config(text="Problem loaded/generated and ready.")
        else:
            self.status_label.config(text="Problem not loaded or generated.")

        self.btn_save.config(state="normal" if self._problem_ready() else "disabled")
        self.btn_simulate.config(
            state=("normal" if self._problem_ready() else "disabled")
        )

    def setup_problem_frame(self):
        defaults = {
            "couriers": 5,
            "vehicles": 3,
            "packages": 20,
        }
        return self.create_integer_form(self.problem_panel, PROBLEM_FIELDS, defaults)

    def setup_simulation_frame(self):
        defaults = {
            "solutions": 10,
            "attempts": 1000,
            "iterations": 500,
        }
        return self.create_integer_form(
            self.simulation_panel, SIMULATION_FIELDS, defaults
        )

    def create_integer_form(self, frame, fields, defaults=None):
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(
                frame,
                text=f"{field.capitalize()}:",
                font=("Arial", 12),
                bg="#f0f0f0",
            ).grid(row=i, column=0, padx=10, pady=8, sticky="e")

            entry = tk.Entry(frame, font=("Arial", 12), width=10)
            entry.grid(row=i, column=1, pady=8)
            entries[field] = entry

            if defaults and field in defaults:
                entry.insert(0, str(defaults[field]))
            else:
                entry.insert(0, "")

            if i == 0:
                entry.focus()

        return entries

    def save(self):
        self.open_path_popup(
            "Save JSON File", self.do_save, default_path=self.json_path
        )

    def load(self):
        self.open_path_popup(
            "Load JSON File", self.do_load, default_path=self.json_path
        )

    def open_path_popup(self, title, callback, default_path=None):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x150")
        popup.grab_set()
        popup.configure(bg="#f0f0f0")

        tk.Label(
            popup,
            text="Enter JSON file path:",
            font=("Arial", 12),
            bg="#f0f0f0",
        ).pack(pady=15)

        entry = tk.Entry(popup, font=("Arial", 12), width=40)
        entry.pack(pady=5, padx=10)
        entry.focus()

        if default_path:
            entry.insert(0, default_path)

        def submit():
            path = entry.get().strip()
            if not path:
                messagebox.showerror("Error", "Path cannot be empty!")
                return
            callback(path)
            popup.destroy()

        submit_btn = tk.Button(
            popup,
            text="Submit",
            command=submit,
            font=("Arial", 12),
            bg="#4caf50",
            fg="white",
            activebackground="#45a049",
            relief="raised",
            bd=3,
        )
        submit_btn.pack(pady=10)

    def do_save(self, path):
        if not self._problem_ready():
            messagebox.showerror("Error", "No generated or loaded problem to save.")
            return

        try:
            self.initializer.save_to_json(path)
            self.json_path = path
            messagebox.showinfo("Done", f"Saved the problem successfully to '{path}'")
        except (PermissionError, OSError) as e:
            messagebox.showerror(
                "Error", f"Couldn't save the problem to '{path}':\n{e}"
            )

    def do_load(self, path):
        try:
            self.initializer.load_from_json(path)
            self.problem = self.initializer.get_problem()
            self.json_path = path

            for field in PROBLEM_FIELDS:
                entry = self.problem_form[field]
                set_text(entry, getattr(self.problem, "n_" + field, ""))

            self.udpate_state()
        except (FileNotFoundError, PermissionError, OSError, Exception) as e:
            messagebox.showerror(
                "Error", f"Couldn't load the problem from '{path}':\n{e}"
            )

    def generate(self):
        problem_data = validate_form(self.problem_form, PROBLEM_FIELDS)

        try:
            couriers = problem_data["couriers"]
            vehicles = problem_data["vehicles"]
            packages = problem_data["packages"]

            self.initializer.generate_random(couriers, vehicles, packages)
            self.problem = self.initializer.get_problem()

            self.udpate_state()

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed:\n{e}")

    def simulate(self):
        simulation_data = validate_form(self.simulation_form, SIMULATION_FIELDS)
        self.udpate_state()

        popup = AnimationPopup(
            self.root, self.problem, simulation_data, self.available_mutations
        )
        self.animation_popups.append(popup)

    def on_root_close(self):
        for popup in self.animation_popups:
            if popup.winfo_exists():
                if popup.anim:
                    popup.anim.event_source.stop()
                    popup.anim = None
                popup.destroy()
        self.animation_popups.clear()
        self.root.destroy()
