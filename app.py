import json
import sys
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty


sys.path.insert(0, os.path.abspath("src"))
from src.problem_initializer import ProblemInitializer
from src.generator import Generator
from src.ga import GA
from src.ui import draw_comparison



class ProblemInputScreen(Screen):
    couriers = ObjectProperty(None)
    vehicles = ObjectProperty(None)
    packages = ObjectProperty(None)
    json_path = ObjectProperty(None)

    def generate(self):
        couriers_num = int(self.couriers.text)
        vehicles_num = int(self.vehicles.text)
        packages_num = int(self.packages.text)

        initializer = ProblemInitializer()
        initializer.generate_random(couriers_num, vehicles_num, packages_num)
        initializer.save_to_json(self.json_path.text)


class ProblemLoaderScreen(Screen):
    json_path = ObjectProperty(None)
    json_content = StringProperty("")
    solutions = ObjectProperty(None)
    attempts = ObjectProperty(None)
    iterations = ObjectProperty(None)

    def run_problem(self):
        initializer = ProblemInitializer()
        initializer.generate_from_json(self.json_path.text)
        solutions_num = int(self.solutions.text)
        attempts_num = int(self.attempts.text)
        iterations_num = int(self.iterations.text)
        problem = initializer.get_problem()
        generator = Generator(problem)
        solutions = generator.generate_many_feasible(solutions_num, attempts_num)

        ga = GA(problem, solutions)

        a, b = ga.run(max_iter=iterations_num)
        print()
        print(f"BEFORE {ga.get_cost(a)}")
        print(a)
        print(f"AFTER {ga.get_cost(b)}")
        print(b)

        print(f"{ga.get_cost(a):.2f}", f"{ga.get_cost(b):.2f}")

        # draw_comparison(a, b)


class ScreenManagement(ScreenManager):
    pass

class OptimizerApp(App):
    def build(self):
        return Builder.load_file("optimizer.kv")


if __name__ == "__main__":
    OptimizerApp().run()