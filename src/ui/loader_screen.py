from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

from src.ui.ui_utils import create_popup, get_number, ValidationError
from src.ui.loaded_problem import LoadedProblem
from src.problem_initializer import ProblemInitializer


class LoaderScreen(Screen):
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
