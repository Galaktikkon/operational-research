import os
import sys
sys.path.insert(0, os.path.abspath("src"))

import tkinter as tk
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.problem_initializer import ProblemInitializer
from src.generator import Generator
from src.ga import GA
from src.ga.mutations import (
    RouteMutation,
    UnusedVehiclesMutation,
    UsedVehiclesMutation,
    PackagesMutation,
    CouriersMutation,
)

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt


import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class AnimationPopup(tk.Toplevel):
    def __init__(self, master, problem_data, sim_params, selected_mutations):
        super().__init__(master)
        self.title("Simulation Animation")
        self.geometry("1400x800")

        # Frame for buttons (Pause + Show Best side by side)
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=5)

        # Pause/Resume Button
        self.is_paused = False
        self.pause_btn = tk.Button(
            self.button_frame,
            text="Pause",
            font=("Arial", 12, "bold"),
            bg="#ff9800",
            fg="white",
            relief="raised",
            bd=3,
            width=10,
            command=self.toggle_pause,
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # Show Best button (starts disabled)
        self.show_best_btn = tk.Button(
            self.button_frame,
            text="Show Best",
            font=("Arial", 12, "bold"),
            bg="#2196f3",
            fg="white",
            relief="raised",
            bd=3,
            width=10,
            command=self.show_best_solution,
            state=tk.DISABLED,
        )
        self.show_best_btn.pack(side=tk.LEFT, padx=5)

        # Back to Simulation button (hidden initially)
        self.back_to_sim_btn = tk.Button(
            self.button_frame,
            text="Back to Simulation",
            font=("Arial", 12, "bold"),
            bg="#4caf50",
            fg="white",
            relief="raised",
            bd=3,
            width=16,
            command=self.back_to_simulation,
        )
        self.back_to_sim_btn.pack_forget()

        # Setup matplotlib figure and canvas
        self.fig, self.axes = plt.subplots(2, 3, figsize=(12, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Frame to hold best solution info and repr widget (split into two columns)
        self.best_view_frame = tk.Frame(self)
        self.best_view_frame.pack_forget()

        # Left side: plot and info box container
        self.left_best_frame = tk.Frame(self.best_view_frame)
        self.left_best_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Right side: repr text widget + scrollbar
        self.right_best_frame = tk.Frame(self.best_view_frame)
        self.right_best_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.repr_text = tk.Text(self.right_best_frame, wrap="none")
        self.repr_text.config(state=tk.DISABLED, width=60, height=25)
        self.repr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_vert = tk.Scrollbar(self.right_best_frame, orient=tk.VERTICAL, command=self.repr_text.yview)
        self.repr_text['yscrollcommand'] = self.scrollbar_vert.set
        self.scrollbar_vert.pack(side=tk.RIGHT, fill=tk.Y)

        # Setup GA & generator (assuming these are given or imported)
        self.generator = Generator(problem_data)
        self.solutions = self.generator.generate_many_feasible(
            sim_params['solutions_num'], sim_params['attempts_num']
        )
        self.ga = GA(problem_data, self.solutions, selected_mutations)
        self.ga_iterator = self.ga.run(max_iter=sim_params['iterations_num'])

        self.initial_best = None
        self.current_best = None
        self.iteration = 0
        self.improvements = 0
        self.sim_params = sim_params
        self.best_found_iteration = 0
        self.selected_mutations = selected_mutations

        self.showing_best = False

        # Variables to hold the best solution figure and canvas
        self.best_fig = None
        self.best_canvas = None

        # Start animation
        self.anim = FuncAnimation(self.fig, self.update_plot, interval=200)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_pause(self):
        if self.is_paused:
            self.anim.event_source.start()
            self.pause_btn.config(text="Pause", bg="#ff9800")
            self.show_best_btn.config(state=tk.DISABLED)
        else:
            self.anim.event_source.stop()
            self.pause_btn.config(text="Resume", bg="#4caf50")
            self.show_best_btn.config(state=tk.NORMAL)
        self.is_paused = not self.is_paused

    def on_close(self):
        if self.anim:
            self.anim.event_source.stop()
            self.anim = None

        if self.best_canvas:
            self.best_canvas.get_tk_widget().destroy()
            self.best_canvas = None

        if self.best_fig:
            plt.close(self.best_fig)
            self.best_fig = None

        self.canvas.get_tk_widget().destroy()
        plt.close(self.fig)
        self.destroy()

    def draw_solution_to_axis(self, solution, axis):
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

    def update_plot(self, frame):
        if self.showing_best:
            return

        try:
            state = next(self.ga_iterator)
        except StopIteration:
            self.anim.event_source.stop()
            return

        if self.initial_best is None:
            self.initial_best = state.solution
            self.current_best = state.solution
        elif self.ga.get_cost(state.solution) < self.ga.get_cost(self.current_best):
            self.current_best = state.solution
            self.improvements += 1
            self.best_found_iteration = self.iteration

        # Clear all axes first
        for ax in self.axes.flatten():
            ax.clear()
            ax.axis('on')  # Make sure axes are visible (for plots)

        # Draw the three top plots
        self.draw_solution_to_axis(self.initial_best, self.axes[0, 0])
        self.axes[0, 0].set(title=f"Initial, cost={self.ga.get_cost(self.initial_best):.2f}")

        self.draw_solution_to_axis(state.solution, self.axes[0, 1])
        self.axes[0, 1].set(title=f"Current, cost={self.ga.get_cost(state.solution):.2f}")

        self.draw_solution_to_axis(self.current_best, self.axes[0, 2])
        self.axes[0, 2].set(title=f"Best, cost={self.ga.get_cost(self.current_best):.2f}")

        # Prepare the info text blocks
        iteration_info = [
            f"Iterations: {self.iteration}/{self.sim_params['iterations_num']}",
            f"Solutions' population: {self.sim_params['solutions_num']}",
            f"Attempts: {self.sim_params['attempts_num']}",
            f"Improvements: {self.improvements}",
            f"Best solution found in: {self.best_found_iteration}",
        ]

        mutation_info = [f"Crossovers: {state.crossok}/{state.crossall}"]
        for m in state.mutations:
            mutation_info.append(f"{m.__name__}: {m.times_feasible_created}/{m.times_run}")

        # Clear bottom row axes and hide axis lines for text boxes
        for ax in self.axes[1]:
            ax.clear()
            ax.axis("off")

        # Put iteration info in bottom-left
        self.axes[1, 0].text(
            0.5,
            0.5,
            "\n".join(iteration_info),
            ha='center',
            va='center',
            fontsize=11,
            linespacing=1.6,
            wrap=True,
            bbox=dict(
                boxstyle='round,pad=1',
                facecolor="#f0f8ff",
                edgecolor='#888888',
                linewidth=2,
                alpha=0.95
            )
        )

        # Put mutation/crossover info in bottom-middle
        self.axes[1, 1].text(
            0.5,
            0.5,
            "\n".join(mutation_info),
            ha='center',
            va='center',
            fontsize=11,
            linespacing=1.6,
            wrap=True,
            bbox=dict(
                boxstyle='round,pad=1',
                facecolor="#f0f8ff",
                edgecolor='#888888',
                linewidth=2,
                alpha=0.95
            )
        )

        # Hide bottom-right axis completely
        self.axes[1, 2].set_visible(False)

        # Redraw canvas
        self.canvas.draw()
        self.iteration += 1


    def show_best_solution(self):
        self.anim.event_source.stop()
        self.showing_best = True

        self.pause_btn.pack_forget()
        self.show_best_btn.pack_forget()
        self.back_to_sim_btn.pack(side=tk.LEFT, padx=5)

        self.canvas.get_tk_widget().pack_forget()

        self.best_view_frame.pack(fill=tk.BOTH, expand=True)

        for widget in self.left_best_frame.winfo_children():
            widget.destroy()

        # Create and store figure and canvas for best solution
        fig_best, ax_best = plt.subplots(figsize=(6, 4))
        self.best_fig = fig_best
        self.best_canvas = FigureCanvasTkAgg(fig_best, master=self.left_best_frame)

        self.draw_solution_to_axis(self.current_best, ax_best)
        ax_best.set(title=f"Best Solution\nCost: {self.ga.get_cost(self.current_best):.2f}")
        fig_best.tight_layout()

        self.best_canvas.draw()
        self.best_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        info_text = "\n".join([
            f"Iterations run: {self.iteration - 1}",
            f"Improvements: {self.improvements}",
            f"Best found at iteration: {self.best_found_iteration}",
            f"Final cost: {self.ga.get_cost(self.current_best):.2f}",
        ])
        info_box = tk.Label(
            self.left_best_frame,
            text=info_text,
            bg="#e3f2fd",
            font=("Arial", 11),
            justify=tk.LEFT,
            anchor="nw",
            relief=tk.SOLID,
            bd=1,
            padx=10,
            pady=5
        )
        info_box.pack(fill=tk.X, pady=10)

        self.repr_text.config(state=tk.NORMAL)
        self.repr_text.delete("1.0", tk.END)
        self.repr_text.insert(tk.END, repr(self.current_best))
        self.repr_text.config(state=tk.DISABLED)

    def back_to_simulation(self):
        self.best_view_frame.pack_forget()

        # Destroy best solution figure and canvas properly
        if self.best_canvas:
            self.best_canvas.get_tk_widget().pack_forget()
            self.best_canvas.get_tk_widget().destroy()
            self.best_canvas = None

        if self.best_fig:
            plt.close(self.best_fig)
            self.best_fig = None

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.back_to_sim_btn.pack_forget()
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.show_best_btn.pack(side=tk.LEFT, padx=5)

        # Do not resume animation automatically
        self.is_paused = True
        self.pause_btn.config(text="Resume", bg="#4caf50")
        self.show_best_btn.config(state=tk.NORMAL)

        self.showing_best = False

class ValidationError(Exception):
    pass


def get_number(text):
    try:
        number = int(text)
    except ValueError:
        raise ValidationError(f"Invalid number: '{text}'")
    if number <= 0:
        raise ValidationError(f"Number '{number}' should be positive")
    return number

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

        self.json_path = "config/base.json"  # default path

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

        # Frame to hold the top two panels side by side
        top_frame = tk.Frame(root, bg="#f0f0f0")
        top_frame.pack(padx=10, pady=10, fill="both", expand=False)

        # Problem Data Panel (left)
        self.problem_panel = tk.LabelFrame(
            top_frame,
            text="Problem Data",
            bg="#d0f0d0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        self.problem_panel.pack(side="left", expand=True, fill="both", padx=10)

        self.problem_info_label = tk.Label(
            self.problem_panel,
            text="No problem data",
            font=("Arial", 12),
            bg="#d0f0d0",  # match panel bg color here
            justify="left",
        )
        self.problem_info_label.pack(anchor="nw")

        # Simulation Data Panel (right)
        self.simulation_panel = tk.LabelFrame(
            top_frame,
            text="Simulation Data",
            bg="#d0f0d0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        self.simulation_panel.pack(side="left", expand=True, fill="both", padx=10)

        self.simulation_info_label = tk.Label(
            self.simulation_panel,
            text="No simulation data",
            font=("Arial", 12),
            bg="#d0f0d0",
            justify="left",
        )
        self.simulation_info_label.pack(anchor="nw")

        # Frame for mutation checkboxes row (full width below top_frame)
        mutations_frame = tk.LabelFrame(
            root,
            text="Mutations",
            bg="#f0f0f0",
            fg="#206020",
            font=("Arial", 14, "bold"),
            padx=15,
            pady=15,
        )
        mutations_frame.pack(padx=10, pady=(0, 20), fill="x")

        self.mutations_frame = mutations_frame
        self.create_mutation_checkboxes()

        # Buttons frame at bottom, two columns
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

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

        for idx, (text, cmd, state) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=cmd, state=state, **btn_style)
            row = idx // 2
            col = idx % 2
            btn.grid(row=row, column=col, padx=15, pady=10)
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
                text=mutation_cls.__name__,
                variable=var,
                bg="#f0f0f0",
                font=("Arial", 11),
                anchor="w",
                justify="left",
                command=self.update_selected_mutations,
            )
            # Grid layout: 3 columns
            row = idx // 3
            col = idx % 3
            chk.grid(row=row, column=col, sticky="w", padx=5, pady=5)
            self.mutation_vars.append((var, mutation_cls))

    def update_selected_mutations(self):
        self.selected_mutations = [
            mutation_cls
            for var, mutation_cls in self.mutation_vars
            if var.get()
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
            state="normal" if self.problem_ready and self.simulation_data else "disabled"
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

        self.problem_data = DummyProblem(data["couriers"], data["vehicles"], data["packages"])
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
        self.open_path_popup("Save JSON File", self.do_save, default_path=self.json_path)

    def load(self):
        self.open_path_popup("Load JSON File", self.do_load, default_path=self.json_path)

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
        entry.pack(pady=5)
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
            messagebox.showerror("Error", f"Couldn't save the problem to '{path}':\n{e}")

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
            messagebox.showerror("Error", f"Couldn't load the problem from '{path}':\n{e}")

    def generate(self):
        if not self.problem_data:
            messagebox.showerror(
                "Error", "Please update the problem data first (couriers, vehicles, packages)."
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
                "Error", "Make sure problem is loaded/generated and simulation data is updated."
            )
            return

        # Clone and transform keys by appending '_num'
        simulation_params = {f"{k}_num": v for k, v in self.simulation_data.items()}

        popup = AnimationPopup(self.root, self.problem_data, simulation_params, self.selected_mutations)
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



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
