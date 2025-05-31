import json

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty



class ProblemInputScreen(Screen):
    couriers = ObjectProperty(None)
    vehicles = ObjectProperty(None)
    packages = ObjectProperty(None)
    solutions = ObjectProperty(None)
    attempts = ObjectProperty(None)
    iterations = ObjectProperty(None)
    json_path = ObjectProperty(None)

    def generate(self):
        print("Generated with:")
        print(f"Couriers: {self.couriers.text}")
        print(f"Vehicles: {self.vehicles.text}")
        print(f"Packages: {self.packages.text}")
        print(f"JSON path: {self.json_path.text}")
        self.couriers.text = ""
        self.vehicles.text = ""
        self.packages.text = ""

class JSONLoaderScreen(Screen):
    json_path = ObjectProperty(None)
    json_content = StringProperty("")

    def load_json_data(self):
        path = self.json_path.text
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.json_content = json.dumps(data, indent=2)
        except Exception as e:
            self.json_content = f"Error loading JSON:\n{e}"

class ScreenManagement(ScreenManager):
    pass

class OptimizerApp(App):
    def build(self):
        return Builder.load_file("optimizer.kv")


if __name__ == "__main__":
    OptimizerApp().run()