import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from generator import Generator
from ga import GA
from .utils import *


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
        self.left_best_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5
        )

        # Right side: repr text widget + scrollbar
        self.right_best_frame = tk.Frame(self.best_view_frame)
        self.right_best_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5
        )

        self.repr_text = tk.Text(self.right_best_frame, wrap="none")
        self.repr_text.config(state=tk.DISABLED, width=60, height=25)
        self.repr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_vert = tk.Scrollbar(
            self.right_best_frame, orient=tk.VERTICAL, command=self.repr_text.yview
        )
        self.repr_text["yscrollcommand"] = self.scrollbar_vert.set
        self.scrollbar_vert.pack(side=tk.RIGHT, fill=tk.Y)

        # Setup GA & generator (assuming these are given or imported)
        self.generator = Generator(problem_data)
        self.solutions = self.generator.generate_many_feasible(
            sim_params["solutions"], sim_params["attempts"]
        )
        self.ga = GA(problem_data, self.solutions, selected_mutations)
        self.ga_iterator = self.ga.run(max_iter=sim_params["iterations"])

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
            ax.axis("on")  # Make sure axes are visible (for plots)

        # Draw the three top plots
        self.draw_solution_to_axis(self.initial_best, self.axes[0, 0])
        self.axes[0, 0].set(
            title=f"Initial, cost={self.ga.get_cost(self.initial_best):.2f}"
        )

        self.draw_solution_to_axis(state.solution, self.axes[0, 1])
        self.axes[0, 1].set(
            title=f"Current, cost={self.ga.get_cost(state.solution):.2f}"
        )

        self.draw_solution_to_axis(self.current_best, self.axes[0, 2])
        self.axes[0, 2].set(
            title=f"Best, cost={self.ga.get_cost(self.current_best):.2f}"
        )

        # Prepare the info text blocks
        iteration_info = [
            f"Iterations: {self.iteration}/{self.sim_params['iterations']}",
            f"Solutions' population: {self.sim_params['solutions']}",
            f"Attempts: {self.sim_params['attempts']}",
            f"Improvements: {self.improvements}",
            f"Best solution found in: {self.best_found_iteration}",
        ]

        mutation_info = [f"Crossovers: {state.crossok}/{state.crossall}"]
        for m in state.mutations:
            mutation_info.append(
                f"{m.__name__}: {m.times_feasible_created}/{m.times_run}"
            )

        # Clear bottom row axes and hide axis lines for text boxes
        for ax in self.axes[1]:
            ax.clear()
            ax.axis("off")

        # Put iteration info in bottom-left
        self.axes[1, 0].text(
            0.5,
            0.5,
            "\n".join(iteration_info),
            ha="center",
            va="center",
            fontsize=11,
            linespacing=1.6,
            wrap=True,
            bbox=dict(
                boxstyle="round,pad=1",
                facecolor="#f0f8ff",
                edgecolor="#888888",
                linewidth=2,
                alpha=0.95,
            ),
        )

        # Put mutation/crossover info in bottom-middle
        self.axes[1, 1].text(
            0.5,
            0.5,
            "\n".join(mutation_info),
            ha="center",
            va="center",
            fontsize=11,
            linespacing=1.6,
            wrap=True,
            bbox=dict(
                boxstyle="round,pad=1",
                facecolor="#f0f8ff",
                edgecolor="#888888",
                linewidth=2,
                alpha=0.95,
            ),
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
        ax_best.set(
            title=f"Best Solution\nCost: {self.ga.get_cost(self.current_best):.2f}"
        )
        fig_best.tight_layout()

        self.best_canvas.draw()
        self.best_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        info_text = "\n".join(
            [
                f"Iterations run: {self.iteration - 1}",
                f"Improvements: {self.improvements}",
                f"Best found at iteration: {self.best_found_iteration}",
                f"Final cost: {self.ga.get_cost(self.current_best):.2f}",
            ]
        )
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
            pady=5,
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
