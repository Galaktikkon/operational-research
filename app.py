import sys
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.factory import Factory
from kivy.properties import ObjectProperty


sys.path.insert(0, os.path.abspath("src"))
from src.problem_initializer import ProblemInitializer
from src.generator import Generator
from src.ga import GA
from src.ui import draw_comparison


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
        except (PermissionError, OSError) as e:
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
        except (FileNotFoundError, PermissionError) as e:
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
        loaded_problem = LoadedProblem(problem, solutions_num, attempts_num, iterations_num)
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

        solutions = generator.generate_many_feasible(loaded_problem.solutions_num,
                                                     loaded_problem.attempts_num)

        ga = GA(loaded_problem.problem, solutions)

        a, b = ga.run(max_iter=loaded_problem.iterations_num)
        print()
        print(f"BEFORE {ga.get_cost(a)}")
        print(a)
        print(f"AFTER {ga.get_cost(b)}")
        print(b)

        print(f"{ga.get_cost(a):.2f}", f"{ga.get_cost(b):.2f}")
        draw_comparison(a, b)