import re

import tkinter as tk
from tkinter import messagebox

from src.problem_initializer import ProblemInitializer
from src.ga.mutations import (
    RouteMutation,
    UnusedVehiclesMutation,
    UsedVehiclesMutation,
    PackagesMutation,
    CouriersMutation,
)

from .utils import *
from .animation_popup import AnimationPopup


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        self.problem_data = None
        self.simulation_data = {}
        self.problem_ready = False

        self.initializer = ProblemInitializer()

        self.json_path = "config/base.json"

        self.available_mutations = [
            RouteMutation,
            UnusedVehiclesMutation,
            UsedVehiclesMutation,
            PackagesMutation,
            CouriersMutation,
        ]
        self.selected_mutations = []

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

        self.problem_info_label = tk.Label(
            self.problem_panel,
            text="No problem data",
            font=("Arial", 12),
            bg="#d0f0d0",
            justify="left",
        )
        self.problem_info_label.pack(anchor="nw")

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

        self.simulation_info_label = tk.Label(
            self.simulation_panel,
            text="No simulation data",
            font=("Arial", 12),
            bg="#d0f0d0",
            justify="left",
        )
        self.simulation_info_label.pack(anchor="nw")

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
        self.create_mutation_checkboxes()

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
            ("Update Problem", self.update_problem, "normal"),
            ("Update Simulation", self.update_simulation, "normal"),
            ("Generate", self.generate, "disabled"),
            ("Save", self.save, "disabled"),
            ("Load", self.load, "normal"),
            ("Simulate", self.simulate, "disabled"),
        ]

        btn_frame.grid_columnconfigure(0, weight=1)
        for idx, (text, cmd, state) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=cmd, state=state, **btn_style)
            row = idx // 2
            col = idx % 2
            btn.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
            setattr(self, f"btn_{text.lower().replace(' ', '_')}", btn)

        self.update_info_labels()
        self.update_buttons_state()

        self.animation_popups = []
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)

    def create_mutation_checkboxes(self):
        self.mutation_vars = []
        # Use a grid with 3 columns to arrange checkboxes nicely
        for idx, mutation_cls in enumerate(self.available_mutations):
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(
                self.mutations_frame,  # updated from self.mutations_panel
                text=re.sub("([a-z])([A-Z])", r"\1 \2", mutation_cls.__name__),
                variable=var,
                bg="#f0f0f0",
                font=("Arial", 11),
                anchor="w",
                justify="left",
                command=self.update_selected_mutations,
            )
            # Grid layout: 3 columns
            row = idx // 1
            col = idx % 1
            chk.grid(row=row, column=col, sticky="w", padx=5, pady=5)
            self.mutation_vars.append((var, mutation_cls))

    def update_selected_mutations(self):
        self.selected_mutations = [
            mutation_cls for var, mutation_cls in self.mutation_vars if var.get()
        ]

    def update_info_labels(self):
        if self.problem_data and hasattr(self.problem_data, "asdict"):
            problem_summary = self.problem_data.asdict()
            problem_text = "\n".join(
                f"{k.capitalize()}: {v}" for k, v in problem_summary.items()
            )
        else:
            problem_text = "No problem data"

        self.problem_info_label.config(text=problem_text)

        if self.simulation_data:
            simulation_text = "\n".join(
                f"{k.capitalize()}: {v}" for k, v in self.simulation_data.items()
            )
        else:
            simulation_text = "No simulation data"

        self.simulation_info_label.config(text=simulation_text)

        if self.problem_ready:
            self.status_label.config(text="Problem loaded/generated and ready.")
        else:
            self.status_label.config(text="Problem not loaded or generated.")

    def update_buttons_state(self):
        self.btn_generate.config(state="normal" if self.problem_data else "disabled")
        self.btn_save.config(state="normal" if self.problem_ready else "disabled")
        self.btn_simulate.config(
            state=(
                "normal" if self.problem_ready and self.simulation_data else "disabled"
            )
        )

    def update_problem(self):
        defaults = {
            "couriers": getattr(self.problem_data, "n_couriers", 5),
            "vehicles": getattr(self.problem_data, "n_vehicles", 3),
            "packages": getattr(self.problem_data, "n_packages", 20),
        }
        self.open_integer_form(
            title="Update Problem",
            fields=["couriers", "vehicles", "packages"],
            callback=self.set_problem_data_from_form,
            defaults=defaults,
        )

    def set_problem_data_from_form(self, data):
        class DummyProblem:
            def __init__(self, couriers, vehicles, packages):
                self.n_couriers = couriers
                self.n_vehicles = vehicles
                self.n_packages = packages

            def asdict(self):
                return {
                    "couriers": self.n_couriers,
                    "vehicles": self.n_vehicles,
                    "packages": self.n_packages,
                }

        self.problem_data = DummyProblem(
            data["couriers"], data["vehicles"], data["packages"]
        )
        self.problem_ready = False
        self.update_info_labels()
        self.update_buttons_state()

    def update_simulation(self):
        defaults = {
            "solutions": self.simulation_data.get("solutions", 10),
            "attempts": self.simulation_data.get("attempts", 1000),
            "iterations": self.simulation_data.get("iterations", 500),
        }
        self.open_integer_form(
            title="Update Simulation",
            fields=["solutions", "attempts", "iterations"],
            callback=self.set_simulation_data,
            defaults=defaults,
        )

    def set_simulation_data(self, data):
        self.simulation_data = data
        self.update_info_labels()
        self.update_buttons_state()

    def open_integer_form(self, title, fields, callback, defaults=None):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("350x250")
        popup.grab_set()
        popup.configure(bg="#f0f0f0")

        entries = {}

        def submit():
            data = {}
            try:
                for field in fields:
                    val = entries[field].get()
                    number = get_number(val)
                    data[field] = number
            except ValidationError as e:
                messagebox.showerror("Invalid input", str(e))
                return
            callback(data)
            popup.destroy()

        for i, field in enumerate(fields):
            tk.Label(
                popup,
                text=f"{field.capitalize()}:",
                font=("Arial", 12),
                bg="#f0f0f0",
            ).grid(row=i, column=0, padx=10, pady=8, sticky="e")

            entry = tk.Entry(popup, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[field] = entry

            if defaults and field in defaults:
                entry.insert(0, str(defaults[field]))
            else:
                entry.insert(0, "")

            if i == 0:
                entry.focus()

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
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=15)

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
        if not self.problem_ready:
            messagebox.showerror("Error", "No generated or loaded problem to save.")
            return

        try:
            self.initializer.save_to_json(path)
            self.json_path = path  # update path
            messagebox.showinfo("Done", f"Saved the problem successfully to '{path}'")
        except (PermissionError, OSError) as e:
            messagebox.showerror(
                "Error", f"Couldn't save the problem to '{path}':\n{e}"
            )

    def do_load(self, path):
        try:
            self.initializer.generate_from_json(path)
            problem = self.initializer.get_problem()
            self.problem_data = problem
            self.problem_ready = True
            self.json_path = path  # update path
            self.update_info_labels()
            self.update_buttons_state()
            messagebox.showinfo("Done", f"Problem loaded from '{path}'")
        except (FileNotFoundError, PermissionError, OSError, Exception) as e:
            messagebox.showerror(
                "Error", f"Couldn't load the problem from '{path}':\n{e}"
            )

    def generate(self):
        if not self.problem_data:
            messagebox.showerror(
                "Error",
                "Please update the problem data first (couriers, vehicles, packages).",
            )
            return

        try:
            couriers_num = getattr(self.problem_data, "n_couriers", None)
            vehicles_num = getattr(self.problem_data, "n_vehicles", None)
            packages_num = getattr(self.problem_data, "n_packages", None)

            self.initializer.generate_random(couriers_num, vehicles_num, packages_num)
            self.problem_data = self.initializer.get_problem()

            self.problem_ready = True
            messagebox.showinfo("Done", "Problem generated successfully.")

            self.update_info_labels()
            self.update_buttons_state()

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed:\n{e}")

    def simulate(self):
        if not (self.problem_ready and self.simulation_data):
            messagebox.showerror(
                "Error",
                "Make sure problem is loaded/generated and simulation data is updated.",
            )
            return

        # Clone and transform keys by appending '_num'
        simulation_params = {f"{k}_num": v for k, v in self.simulation_data.items()}

        popup = AnimationPopup(
            self.root, self.problem_data, simulation_params, self.selected_mutations
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
