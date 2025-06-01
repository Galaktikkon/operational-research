import os

from kivy.uix.screenmanager import ScreenManager
from kivy.app import App
from kivy.lang.builder import Builder

from src.ui.input_screen import InputScreen
from src.ui.loader_screen import LoaderScreen
from src.ui.animation_screen import AnimationScreen


class OptimizerApp(App):
    loaded_problem = None

    def build(self):
        Builder.load_file(os.path.join(os.path.dirname(__file__), "optimizer.kv"))
        management = ScreenManager()
        management.add_widget(InputScreen(name="problem_input"))
        management.add_widget(LoaderScreen(name="problem_loader"))
        management.add_widget(AnimationScreen(name="animation"))
        return management
