import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import tkinter as tk
from tkinter import messagebox

from src.problem_initializer import ProblemInitializer

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")
        self.root.geometry("800x600")

        # Store the ProblemInitializer instance here after load or generate
        self.initializer = None

        # Data dictionaries to store integer values from forms
        self.problem_data = {}
        self.simulation_data = {}
        self.json_path = None

        # Info label to show current data
        self.info_label = tk.Label(root, text="No problem or simulation data yet.", font=("Arial", 14), justify="left")
        self.info_label.pack(pady=10)

        # Buttons container frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        # Update Problem button
        self.btn_update_problem = tk.Button(btn_frame, text="Update Problem", width=15, command=self.update_problem)
        self.btn_update_problem.grid(row=0, column=0, padx=5, pady=5)

        # Update Simulation button
        self.btn_update_simulation = tk.Button(btn_frame, text="Update Simulation", width=15, command=self.update_simulation)
        self.btn_update_simulation.grid(row=0, column=1, padx=5, pady=5)

        # Save button - start disabled
        self.btn_save = tk.Button(btn_frame, text="Save", width=15, command=self.save, state="disabled")
        self.btn_save.grid(row=0, column=2, padx=5, pady=5)

        # Load button
        self.btn_load = tk.Button(btn_frame, text="Load", width=15, command=self.load)
        self.btn_load.grid(row=0, column=3, padx=5, pady=5)

        # Generate button
        self.btn_generate = tk.Button(btn_frame, text="Generate", width=15, command=self.generate)
        self.btn_generate.grid(row=1, column=0, padx=5, pady=5)

        # Simulate button - start disabled
        self.btn_simulate = tk.Button(btn_frame, text="Simulate", width=15, command=self.simulate, state="disabled")
        self.btn_simulate.grid(row=1, column=1, padx=5, pady=5)

    def update_info_label(self):
        problem_str = ", ".join(f"{k}: {v}" for k, v in self.problem_data.items()) or "No problem data"
        simulation_str = ", ".join(f"{k}: {v}" for k, v in self.simulation_data.items()) or "No simulation data"
        json_str = self.json_path or "No JSON file loaded"
        self.info_label.config(text=f"Problem: {problem_str}\nSimulation: {simulation_str}\nJSON file: {json_str}")

    def update_problem(self):
        self.open_integer_form(
            title="Update Problem",
            fields=["couriers", "vehicles", "packages"],
            callback=self.set_problem_data
        )

    def update_simulation(self):
        self.open_integer_form(
            title="Update Simulation",
            fields=["solutions", "attempts", "iterations"],
            callback=self.set_simulation_data
        )

    def open_integer_form(self, title, fields, callback):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("350x250")
        popup.grab_set()

        entries = {}

        def submit():
            data = {}
            for field in fields:
                val = entries[field].get()
                if not val.isdigit():
                    messagebox.showerror("Invalid input", f"'{field}' must be an integer!")
                    return
                data[field] = int(val)
            callback(data)
            popup.destroy()

        for i, field in enumerate(fields):
            tk.Label(popup, text=f"{field.capitalize()}:", font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=8, sticky="e")
            entry = tk.Entry(popup, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[field] = entry
            if i == 0:
                entry.focus()

        submit_btn = tk.Button(popup, text="Submit", command=submit, font=("Arial", 12))
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=15)

    def set_problem_data(self, data):
        self.problem_data = data
        self.update_info_label()

    def set_simulation_data(self, data):
        self.simulation_data = data
        self.update_info_label()

    def save(self):
        if not self.initializer:
            messagebox.showerror("Error", "No problem initializer loaded or generated.")
            return
        self.open_path_popup("Save JSON File", self.do_save)

    def load(self):
        self.open_path_popup("Load JSON File", self.do_load)

    def open_path_popup(self, title, callback):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x150")
        popup.grab_set()

        tk.Label(popup, text="Enter JSON file path:", font=("Arial", 12)).pack(pady=15)

        entry = tk.Entry(popup, font=("Arial", 12), width=40)
        entry.pack(pady=5)
        entry.focus()

        def submit():
            path = entry.get().strip()
            if not path:
                messagebox.showerror("Error", "Path cannot be empty!")
                return
            callback(path)
            popup.destroy()

        submit_btn = tk.Button(popup, text="Submit", command=submit, font=("Arial", 12))
        submit_btn.pack(pady=10)

    def do_save(self, path):
        try:
            self.initializer.save_to_json(path)
            self.json_path = path
            messagebox.showinfo("Saved", f"Problem saved to {path}")
            self.update_info_label()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save problem: {e}")

    def do_load(self, path):
        try:
            self.initializer = ProblemInitializer.load_from_json(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load problem: {e}")
            return

        try:
            problem = self.initializer.get_problem()
            # Assuming problem is dict with keys couriers, vehicles, packages, etc.
            self.problem_data = problem
            # Clear simulation data on load (or adapt if you want)
            self.simulation_data = {}
            self.json_path = path
            messagebox.showinfo("Loaded", f"Problem loaded from {path}")
            self.update_info_label()

            # Enable Save and Simulate buttons after load
            self.btn_save.config(state="normal")
            self.btn_simulate.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process problem data: {e}")

    def generate(self):
        if not self.problem_data:
            messagebox.showerror("Error", "Please update the problem data first (couriers, vehicles, packages).")
            return

        try:
            couriers_num = self.problem_data.get("couriers")
            vehicles_num = self.problem_data.get("vehicles")
            packages_num = self.problem_data.get("packages")

            self.initializer = ProblemInitializer()
            self.initializer.generate_random(couriers_num, vehicles_num, packages_num)

            # Note: per your request, do NOT save automatically on generate

            messagebox.showinfo("Done", f"Problem generated (not saved).")

            # Enable Save and Simulate buttons after generating
            self.btn_save.config(state="normal")
            self.btn_simulate.config(state="normal")

            # Also update problem_data from initializer.get_problem() to sync
            problem = self.initializer.get_problem()
            self.problem_data = problem
            self.update_info_label()

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {e}")

    def simulate(self):
        # Dummy simulate action for demo
        messagebox.showinfo("Simulation", "Simulation started with current data!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
