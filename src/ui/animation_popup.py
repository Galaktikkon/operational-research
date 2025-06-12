import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ga.mutations import *
from generator import Generator
from ga import GA
from .utils import *


class AnimationPopup(tk.Toplevel):
    def __init__(self, master, problem, sim_params, on_popup_close):
        super().__init__(master)
        self.root = master
        self.title("Simulation Animation")
        self.geometry("1400x700")

        self.problem = problem
        self.on_popup_close = on_popup_close

        self.fig, self.axes = plt.subplots(1, 3, figsize=(16, 2))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(pady=20, fill="x")

        self.mutations_frame = tk.Frame(self.bottom_frame)
        self.mutations_frame.pack(side="left", expand=True)

        mutations: list[type[Mutation]] = [
            CouriersMutation,
            UsedVehiclesMutation,
            UnusedVehiclesMutation,
            PackagesMutation,
            RouteMutation,
        ]

        self.popups = []
        self.labels = {}

        mutation_info = [f"Crossovers"]
        for m in mutations:
            m.times_feasible_created = 0
            m.times_run = 0
            mutation_info.append(f"{m.__name__}")

        for r, i in enumerate(mutation_info):
            h = format_mutation_name(i)
            tk.Label(
                self.mutations_frame, text=h + ":", font=("Arial", 12, "bold")
            ).grid(row=r, column=0, padx=10, sticky="w")
            l = tk.Label(self.mutations_frame, text="0/0", font=("Arial", 12, "bold"))
            l.grid(row=r, column=1, padx=10, sticky="e")
            self.labels[i] = l

        self.info_frame = tk.Frame(self.bottom_frame)
        self.info_frame.pack(side="left", expand=True)

        stats = [
            "Iterations",
            "Improvements",
            "Best found in",
        ]
        for r, i in enumerate(stats):
            tk.Label(
                self.info_frame, text=i + ":", padx=10, font=("Arial", 12, "bold")
            ).grid(row=r, column=0, sticky="w")
            l = tk.Label(
                self.info_frame, text="0/0", padx=10, font=("Arial", 12, "bold")
            )
            l.grid(row=r, column=1, sticky="e")
            self.labels[i] = l

        self.legend_frame = tk.Frame(self.bottom_frame)
        self.legend_frame.pack(side="left", expand=True)

        for j in range(problem.n_vehicles):
            canvas = tk.Canvas(self.legend_frame, width=12, height=12)
            color = get_mpl_color(j)
            canvas.create_oval(1, 1, 11, 11, fill=color, outline=color)
            canvas.grid(row=j, column=0, sticky="w")
            tk.Label(
                self.legend_frame, text=f"Vehicle {j}", padx=10, font=("Arial", 12)
            ).grid(row=j, column=1, sticky="e")

        self.button_frame = tk.Frame(self.bottom_frame)
        self.button_frame.pack(side="left", expand=True)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(1, weight=1)
        self.button_frame.grid_rowconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)

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
        self.pause_btn.grid(row=0, column=0, padx=5)

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
        )
        self.show_best_btn.grid(row=1, column=0, padx=5)

        self.show_problem_btn = tk.Button(
            self.button_frame,
            text="Show Problem",
            font=("Arial", 12, "bold"),
            bg="#2196f3",
            fg="white",
            relief="raised",
            bd=3,
            width=10,
            command=self.show_problem,
        )
        self.show_problem_btn.grid(row=2, column=0, padx=5)

        # Setup GA & generator (assuming these are given or imported)
        self.generator = Generator(problem)
        self.solutions = self.generator.generate_many_feasible(
            sim_params["solutions"], sim_params["attempts"]
        )
        self.ga = GA(problem, self.solutions, sim_params["C"], sim_params["alpha"])
        self.ga_iterator = self.ga.run(max_iter=sim_params["iterations"])

        self.initial_best = None
        self.current_best = None
        self.iteration = 0
        self.improvements = 0
        self.sim_params = sim_params
        self.best_found_iteration = 0

        self.showing_best = False

        # Variables to hold the best solution figure and canvas
        self.best_fig = None
        self.best_canvas = None

        # Start animation
        self.anim = FuncAnimation(
            self.fig, self.update_plot, interval=sim_params["animation delay"]
        )
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_pause(self):
        if self.is_paused:
            self.anim.event_source.start()
            self.pause_btn.config(text="Pause", bg="#ff9800")
        else:
            self.anim.event_source.stop()
            self.pause_btn.config(text="Resume", bg="#4caf50")
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

        for p in self.popups:
            p.destroy()

        self.canvas.get_tk_widget().destroy()
        plt.close(self.fig)
        self.destroy()
        self.on_popup_close()

    def update_plot(self, _):
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

            draw_solution_to_axis(self.initial_best, self.axes[0])
            self.axes[0].set(
                title=f"Initial, cost={self.ga.get_cost(self.initial_best):.2f}"
            )
        elif self.ga.get_cost(state.solution) < self.ga.get_cost(self.current_best):
            self.current_best = state.solution

            if hasattr(self, "best_text") and self.best_text.winfo_exists():
                self.best_text.config(state=tk.NORMAL)
                self.best_text.delete("1.0", tk.END)
                self.best_text.insert(tk.END, repr(self.current_best))
                self.best_text.config(state=tk.DISABLED)

            self.improvements += 1
            self.best_found_iteration = self.iteration

        self.axes[1].clear()

        draw_solution_to_axis(state.solution, self.axes[1])
        self.axes[1].set(
            title=f"Current best, cost={self.ga.get_cost(state.solution):.2f}"
        )

        iter_text = f"{self.iteration}/{self.sim_params['iterations']}"
        self.labels["Iterations"].config(text=iter_text)
        self.labels["Improvements"].config(text=f"{self.improvements}")
        self.labels["Best found in"].config(text=f"{self.best_found_iteration}")

        self.labels["Crossovers"].config(text=f"{state.crossok}/{state.crossall}")
        for m in state.mutations:
            self.labels[m.__name__].config(
                text=f"{m.times_feasible_created}/{m.times_run}"
            )

        # Redraw canvas
        self.canvas.draw()
        self.iteration += 1

    def create_text_popup(self, title, text):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("1024x768")
        popup.configure(bg="#f0f0f0")

        text_frame = tk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        repr_text = tk.Text(text_frame, wrap="none")
        repr_text.config(state=tk.DISABLED, width=60, height=20)
        repr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_vert = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=repr_text.yview
        )
        repr_text["yscrollcommand"] = scrollbar_vert.set
        scrollbar_vert.pack(side=tk.RIGHT, fill=tk.Y)

        repr_text.config(state=tk.NORMAL)
        repr_text.delete("1.0", tk.END)
        repr_text.insert(tk.END, text)
        repr_text.config(state=tk.DISABLED)

        self.popups.append(popup)
        return repr_text

    def show_best_solution(self):
        self.best_text = self.create_text_popup(
            "Best Solution", repr(self.current_best) if self.current_best else ""
        )

    def show_problem(self):
        self.create_text_popup("Problem Description", repr(self.problem))
