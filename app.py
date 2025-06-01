import sys
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath("src"))
from src.problem_initializer import ProblemInitializer
from src.generator import Generator
from src.ga import GA
from src.ui import draw_solution_to_axis


class LoadedProblem:
    def __init__(self, problem, solutions_num, attempts_num, iterations_num):
        self.problem = problem
        self.solutions_num = solutions_num
        self.attempts_num = attempts_num
        self.iterations_num = iterations_num


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


def create_popup(title, message):
    popup = Factory.InfoPopup()
    popup.title = title
    popup.ids.message_label.text = message
    popup.open()


class ProblemInputScreen(Screen):
    couriers = ObjectProperty(None)
    vehicles = ObjectProperty(None)
    packages = ObjectProperty(None)
    json_path = ObjectProperty(None)

    def generate(self):
        try:
            couriers_num = get_number(self.couriers.text)
            vehicles_num = get_number(self.vehicles.text)
            packages_num = get_number(self.packages.text)
        except ValidationError as e:
            create_popup("Error", str(e))
            return

        initializer = ProblemInitializer()
        initializer.generate_random(couriers_num, vehicles_num, packages_num)
        try:
            initializer.save_to_json(self.json_path.text)
        except (PermissionError, OSError):
            create_popup("Error", f"Couldn't save the problem to {self.json_path.text}")
            return

        create_popup("Done", f"Saved the problem to {self.json_path.text}")


class ProblemLoaderScreen(Screen):
    json_path = ObjectProperty(None)
    solutions = ObjectProperty(None)
    attempts = ObjectProperty(None)
    iterations = ObjectProperty(None)

    def run_problem(self):
        initializer = ProblemInitializer()
        try:
            initializer.generate_from_json(self.json_path.text)
        except (FileNotFoundError, PermissionError):
            create_popup("Error", f"Couldn't load file '{self.json_path.text}'")
            return

        try:
            solutions_num = get_number(self.solutions.text)
            attempts_num = get_number(self.attempts.text)
            iterations_num = get_number(self.iterations.text)
        except ValidationError as e:
            create_popup("Error", str(e))
            return

        problem = initializer.get_problem()
        app = App.get_running_app()
        app.loaded_problem = LoadedProblem(problem, solutions_num, attempts_num, iterations_num)

        self.manager.current = "animation"


class GAAnimationScreen(Screen):
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

        self.fig, self.axes = plt.subplots(1, 3, figsize=(12, 4))
        self.canvas = FigureCanvasKivyAgg(self.fig)

        plot_box = self.ids.plot_box
        plot_box.clear_widgets()
        plot_box.add_widget(self.canvas)

        Clock.schedule_interval(self.update_plot, 0.2)

    def update_plot(self, dt):
        try:
            solution = next(self.ga_iterator)
        except StopIteration:
            Clock.unschedule(self.update_plot)
            return

        if self.initial_best is None:
            self.initial_best = solution
        if self.current_best is None or self.ga.get_cost(solution) < self.ga.get_cost(self.current_best):
            self.current_best = solution

        for axis in self.axes:
            axis.clear()

        draw_solution_to_axis(self.initial_best, self.axes[0])
        self.axes[0].set(title=f"Initial, cost={self.ga.get_cost(self.initial_best):.2f}")

        draw_solution_to_axis(solution, self.axes[1])
        self.axes[1].set(title=f"Current, cost={self.ga.get_cost(solution):.2f}")

        draw_solution_to_axis(self.current_best, self.axes[2])
        self.axes[2].set(title=f"Best, cost={self.ga.get_cost(self.current_best):.2f}")

        self.canvas.draw()


class ScreenManagement(ScreenManager):
    pass


class OptimizerApp(App):
    loaded_problem = None

    def build(self):
        management = ScreenManagement()
        management.add_widget(ProblemInputScreen(name="problem_input"))
        management.add_widget(ProblemLoaderScreen(name="problem_loader"))
        management.add_widget(GAAnimationScreen(name="animation"))
        return management


if __name__ == "__main__":
    OptimizerApp().run()
