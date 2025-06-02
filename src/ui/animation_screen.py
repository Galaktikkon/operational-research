from kivy.app import App
from kivy.uix.screenmanager import Screen
import matplotlib.pyplot as plt
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock


from src.generator import Generator
from src.ga import GA


class AnimationScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        loaded_problem = app.loaded_problem

        self.generator = Generator(loaded_problem.problem)
        self.solutions = self.generator.generate_many_feasible(
            loaded_problem.solutions_num,
            loaded_problem.attempts_num
        )
        self.ga = GA(loaded_problem.problem, self.solutions)
        self.ga_iterator = self.ga.run(max_iter=loaded_problem.iterations_num)
        self.initial_best = None
        self.current_best = None

        self.fig, self.axes = plt.subplots(2, 3, figsize=(12, 4))
        self.canvas = FigureCanvasKivyAgg(self.fig)

        plot_box = self.ids.plot_box
        plot_box.clear_widgets()
        plot_box.add_widget(self.canvas)

        Clock.schedule_interval(self.update_plot, 0.2)

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
                

    def update_plot(self, dt):
        app = App.get_running_app()
        loaded_problem = app.loaded_problem
        app.iterations = min(app.iterations + 1, loaded_problem.iterations_num)

        try:
            state = next(self.ga_iterator)
        except StopIteration:
            Clock.unschedule(self.update_plot)
            return

        if self.initial_best is None:
            self.initial_best = state.solution
        if self.current_best is None or self.ga.get_cost(state.solution) < self.ga.get_cost(self.current_best):
            self.current_best = state.solution
            app.improvements += 1

        for ax in self.axes.flatten():
            ax.clear()


        self.draw_solution_to_axis(self.initial_best, self.axes[0, 0])
        self.axes[0, 0].set(title=f"Initial, cost={self.ga.get_cost(self.initial_best):.2f}")

        self.draw_solution_to_axis(state.solution, self.axes[0, 1])
        self.axes[0, 1].set(title=f"Current, cost={self.ga.get_cost(state.solution):.2f}")

        self.draw_solution_to_axis(self.current_best, self.axes[0, 2])
        self.axes[0, 2].set(title=f"Best, cost={self.ga.get_cost(self.current_best):.2f}")


        content_first = [
            f"Iterations: {app.iterations}/{loaded_problem.iterations_num}",
            f"Max Attempts: {loaded_problem.attempts_num}",
            f"Solutions: {loaded_problem.solutions_num}",
            f"Improvements: {app.improvements}"
        ]

        content_second = [f"Crossovers: {state.crossok}/{state.crossall}",]
        for m in state.mutations:
            to_add = f"{m.__name__}: {m.times_feasible_created}/{m.times_run}"
            content_second.append(to_add)

        content = [
            "\n".join(content_first),
            "\n".join(content_second)
        ]

        colors = ("#f0f8ff", "#f0f8ff")

        stats_config = [
            {"content": content, "bgcolor": color}
            for content, color in zip(content, colors)
        ]
        
        for col, config in enumerate(stats_config):
            ax = self.axes[1, col]
            
            ax.text(0.5, 0.5, config['content'], 
                ha='center', va='center', 
                fontsize=self.fig.get_size_inches()[0],
                linespacing=1.5,
                bbox=dict(boxstyle='round,pad=1', 
                            facecolor=config['bgcolor'],
                            edgecolor='#888888',
                            linewidth=2,
                            alpha=0.9))
            
        for ax in self.axes[1]:
            ax.axis('off')

        self.canvas.draw()
