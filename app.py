import os
import sys

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")
from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager

sys.path.insert(0, os.path.abspath("src"))
from src.ga import GA
from src.generator import Generator
from src.problem_initializer import ProblemInitializer
from src.ui import draw_solution_to_axis


class LoadedProblem:
    def __init__(self, problem, solutions_num, attempts_num, iterations_num):
        self.problem = problem
        self.solutions_num = solutions_num
        self.attempts_num = attempts_num
        self.iterations_num = iterations_num


loaded_problem = None


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
        global loaded_problem
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
        loaded_problem = LoadedProblem(
            problem, solutions_num, attempts_num, iterations_num
        )
        self.get_root_window().close()


class ScreenManagement(ScreenManager):
    pass


class OptimizerApp(App):
    def build(self):
        management = ScreenManagement()
        management.add_widget(ProblemInputScreen(name="problem_input"))
        management.add_widget(ProblemLoaderScreen(name="problem_loader"))
        return management


if __name__ == "__main__":
    app = OptimizerApp()
    app.run()

    if loaded_problem is not None:
        generator = Generator(loaded_problem.problem)

        solutions = generator.generate_many_feasible(
            loaded_problem.solutions_num, loaded_problem.attempts_num
        )

        ga = GA(loaded_problem.problem, solutions)

        initial_best = None
        current_best = None

        plt.ion()
        fig, axes = plt.subplots(1, 3, figsize=(24, 7))
        plt.show()
        for solution in ga.run(max_iter=loaded_problem.iterations_num):
            # print(solution)
            if initial_best is None:
                initial_best = solution
            if current_best is None or ga.get_cost(solution) < ga.get_cost(
                current_best
            ):
                current_best = solution
            for axis in axes:
                axis.clear()
            draw_solution_to_axis(initial_best, axes[0])
            axes[0].set(title=f"Initial solution, cost={ga.get_cost(initial_best):.2f}")
            draw_solution_to_axis(solution, axes[1])
            axes[1].set(title=f"Current solution, cost={ga.get_cost(solution):.2f}")
            draw_solution_to_axis(current_best, axes[2])
            axes[2].set(title=f"Best solution, cost={ga.get_cost(current_best):.2f}")

            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.001)
        plt.ioff()
        plt.show()
